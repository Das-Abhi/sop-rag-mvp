"""
Document processing tasks for background processing
"""
from celery import shared_task, current_task
from loguru import logger
import os
import time
from pathlib import Path

# Import services (will be initialized when needed)
from app.services.vector_store import VectorStore
from app.core.embedding_service import EmbeddingService
from app.core.layout_analyzer import LayoutAnalyzer
from app.core.text_extractor import TextExtractor
from app.core.chunking_engine import ChunkingEngine


@shared_task(bind=True, name="app.tasks.document_tasks.process_document")
def process_document(self, document_id: str, file_path: str, document_type: str = "pdf"):
    """
    Main document processing task

    Args:
        document_id: Unique document identifier
        file_path: Path to document file
        document_type: Type of document (pdf, docx, txt)

    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Starting document processing: {document_id}")
        total_steps = 5

        # Step 1: Validate file
        self.update_state(
            state="PROGRESS",
            meta={"step": 1, "total_steps": total_steps, "message": "Validating document"}
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        file_size = os.path.getsize(file_path)
        logger.info(f"Document size: {file_size} bytes")

        # Step 2: Extract layout
        self.update_state(
            state="PROGRESS",
            meta={"step": 2, "total_steps": total_steps, "message": "Analyzing document layout"}
        )

        layout_analyzer = LayoutAnalyzer()
        regions = []

        if document_type == "pdf":
            # Analyze PDF layout
            page_count = 0
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    page_count = len(pdf_reader.pages)
                logger.info(f"PDF has {page_count} pages")
            except Exception as e:
                logger.warning(f"Error reading PDF page count: {e}")

        # Step 3: Extract content
        self.update_state(
            state="PROGRESS",
            meta={"step": 3, "total_steps": total_steps, "message": "Extracting content"}
        )

        text_extractor = TextExtractor()
        # Extract text from the document
        if document_type == "pdf":
            try:
                extracted_text = text_extractor.extract_page(file_path, 0)
            except Exception as e:
                logger.error(f"Error extracting text: {e}")
                extracted_text = ""
        else:
            # For other formats, read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                extracted_text = f.read()

        logger.info(f"Extracted {len(extracted_text)} characters")

        # Step 4: Create chunks
        self.update_state(
            state="PROGRESS",
            meta={"step": 4, "total_steps": total_steps, "message": "Creating semantic chunks"}
        )

        # Extract filename from file_path for metadata
        filename = os.path.basename(file_path).replace(".pdf", "").replace(".txt", "").replace(".docx", "")

        chunking_engine = ChunkingEngine()
        chunks = chunking_engine.chunk_text(
            extracted_text,
            document_id,
            metadata={
                "source_file": filename,
                "document_id": document_id,
                "page_num": 0  # Default to page 0, can be enhanced for multi-page PDFs
            }
        )
        logger.info(f"Created {len(chunks)} chunks with metadata")

        # Step 5: Generate embeddings and index
        self.update_state(
            state="PROGRESS",
            meta={"step": 5, "total_steps": total_steps, "message": "Generating embeddings"}
        )

        # Convert chunks to serializable dicts for Celery
        chunks_data = [
            {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "chunk_type": chunk.chunk_type,
                "token_count": chunk.token_count,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]

        # Update document in database with chunk counts
        from app.database import SessionLocal
        from app.crud import DocumentCRUD
        db = SessionLocal()
        try:
            DocumentCRUD.update_chunk_counts(db, document_id, len(chunks), 0, 0)
            DocumentCRUD.update_status(db, document_id, "processing")
            db.commit()
            logger.info(f"Updated chunk counts in DB: {len(chunks)} text chunks")

            # Notify connected clients about status change via WebSocket
            try:
                from app.services.task_updates import send_processing_update_sync
                send_processing_update_sync(document_id, "processing", len(chunks))
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update: {e}")
        finally:
            db.close()

        # Call embedding task
        embedding_result = generate_embeddings.delay(document_id, chunks_data)
        logger.info(f"Embedding task queued: {embedding_result.id}")

        result = {
            "document_id": document_id,
            "status": "processing",
            "chunk_count": len(chunks),
            "text_chunks": len(chunks),
            "image_chunks": 0,
            "table_chunks": 0,
            "processing_time": time.time(),
            "embedding_task_id": embedding_result.id
        }

        logger.info(f"Document processing step completed: {document_id}")
        return result

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        # Update status to error and notify clients
        try:
            from app.database import SessionLocal
            from app.crud import DocumentCRUD
            from app.services.task_updates import send_processing_update_sync
            db = SessionLocal()
            try:
                DocumentCRUD.update_status(db, document_id, "error", str(e))
                db.commit()
                send_processing_update_sync(document_id, "error", 0, str(e))
            finally:
                db.close()
        except Exception as notify_err:
            logger.warning(f"Failed to update error status: {notify_err}")

        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@shared_task(bind=True, name="app.tasks.document_tasks.generate_embeddings")
def generate_embeddings(self, document_id: str, chunks: list):
    """
    Generate embeddings for document chunks

    Args:
        document_id: Document identifier
        chunks: List of chunk objects

    Returns:
        Dictionary with embedding results
    """
    try:
        logger.info(f"Starting embedding generation for {document_id}")

        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        total_chunks = len(chunks)
        processed = 0

        # Prepare chunks for vector store
        chunks_with_embeddings = []

        for i, chunk_data in enumerate(chunks):
            if i % 10 == 0:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "document_id": document_id,
                        "processed": i,
                        "total": total_chunks,
                        "message": f"Embedding chunks {i}/{total_chunks}"
                    }
                )

            try:
                # Generate embedding for chunk
                embedding = embedding_service.embed_text(chunk_data["content"])

                chunk_dict = {
                    "id": chunk_data["chunk_id"],
                    "chunk_id": chunk_data["chunk_id"],
                    "content": chunk_data["content"],
                    "embedding": embedding,
                    "metadata": {
                        "document_id": document_id,
                        "chunk_type": chunk_data.get("chunk_type", "text"),
                        "token_count": chunk_data.get("token_count", 0),
                        **chunk_data.get("metadata", {})
                    }
                }
                chunks_with_embeddings.append(chunk_dict)
                processed += 1

            except Exception as e:
                logger.warning(f"Error embedding chunk {chunk_data.get('chunk_id', 'unknown')}: {e}")

        # Index chunks in vector store
        collection = "text_chunks"
        success = vector_store.add_chunks(collection, chunks_with_embeddings)

        if not success:
            raise Exception("Failed to add chunks to vector store")

        # Mark document as completed in database
        from app.database import SessionLocal
        from app.crud import DocumentCRUD
        db = SessionLocal()
        try:
            DocumentCRUD.update_status(db, document_id, "completed")
            db.commit()
            logger.info(f"Marked document {document_id} as completed")

            # Notify connected clients about completion via WebSocket
            try:
                from app.services.task_updates import send_processing_update_sync
                send_processing_update_sync(document_id, "completed", total_chunks)
            except Exception as e:
                logger.warning(f"Failed to send completion update: {e}")
        finally:
            db.close()

        result = {
            "document_id": document_id,
            "status": "completed",
            "total_chunks": total_chunks,
            "processed_chunks": processed,
            "collection": collection
        }

        logger.info(f"Embeddings completed for {document_id}: {processed} chunks")
        return result

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        # Update status to error and notify clients
        try:
            from app.database import SessionLocal
            from app.crud import DocumentCRUD
            from app.services.task_updates import send_processing_update_sync
            db = SessionLocal()
            try:
                DocumentCRUD.update_status(db, document_id, "error", str(e))
                db.commit()
                send_processing_update_sync(document_id, "error", 0, str(e))
            finally:
                db.close()
        except Exception as notify_err:
            logger.warning(f"Failed to update embedding error status: {notify_err}")

        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@shared_task(bind=True, name="app.tasks.document_tasks.index_chunks")
def index_chunks(self, document_id: str, chunks: list, collection: str = "text_chunks"):
    """
    Index chunks in vector store

    Args:
        document_id: Document identifier
        chunks: List of chunks with embeddings
        collection: Target collection

    Returns:
        Indexing results
    """
    try:
        logger.info(f"Indexing {len(chunks)} chunks in {collection}")

        vector_store = VectorStore()
        success = vector_store.add_chunks(collection, chunks)

        if not success:
            raise Exception(f"Failed to index chunks in {collection}")

        result = {
            "document_id": document_id,
            "collection": collection,
            "indexed_chunks": len(chunks),
            "status": "success"
        }

        logger.info(f"Indexing completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error indexing chunks: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@shared_task(name="app.tasks.document_tasks.cleanup_old_results")
def cleanup_old_results():
    """
    Cleanup old Celery results from Redis
    """
    try:
        from celery.result import AsyncResult
        logger.info("Cleaning up old Celery results")
        # Results older than 1 day will be automatically purged by Redis TTL
        logger.info("Cleanup completed")
        return {"status": "success", "message": "Old results cleaned"}
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {"status": "error", "message": str(e)}
