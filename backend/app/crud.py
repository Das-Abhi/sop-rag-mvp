"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from app.models import Document, Chunk, ProcessingTask, QueryLog
from datetime import datetime
from loguru import logger
from typing import List, Optional


class DocumentCRUD:
    """CRUD operations for documents"""

    @staticmethod
    def create(db: Session, document_id: str, title: str, file_path: str, file_size: int, file_type: str = "pdf"):
        """Create a new document"""
        doc = Document(
            document_id=document_id,
            title=title,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info(f"Document created: {document_id}")
        return doc

    @staticmethod
    def get(db: Session, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        return db.query(Document).filter(Document.document_id == document_id).first()

    @staticmethod
    def list_all(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[Document]:
        """List documents with optional status filter"""
        query = db.query(Document)
        if status:
            query = query.filter(Document.status == status)
        return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_status(db: Session, document_id: str, status: str, error_message: str = None):
        """Update document status"""
        doc = DocumentCRUD.get(db, document_id)
        if doc:
            doc.status = status
            doc.updated_at = datetime.utcnow()
            if error_message:
                doc.error_message = error_message
            if status == "completed":
                doc.processed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Document {document_id} status updated to {status}")
        return doc

    @staticmethod
    def update_chunk_counts(db: Session, document_id: str, text_chunks: int = 0, image_chunks: int = 0, table_chunks: int = 0):
        """Update chunk counts"""
        doc = DocumentCRUD.get(db, document_id)
        if doc:
            doc.text_chunks = text_chunks
            doc.image_chunks = image_chunks
            doc.table_chunks = table_chunks
            doc.total_chunks = text_chunks + image_chunks + table_chunks
            db.commit()
            logger.info(f"Document {document_id} chunk counts updated")
        return doc

    @staticmethod
    def delete(db: Session, document_id: str):
        """Delete document and related chunks"""
        doc = DocumentCRUD.get(db, document_id)
        if doc:
            db.delete(doc)
            db.commit()
            logger.info(f"Document deleted: {document_id}")
            return True
        return False

    @staticmethod
    def delete_with_embeddings(db: Session, document_id: str, vector_store=None, cache_manager=None):
        """
        Delete document from all storage systems (PostgreSQL, ChromaDB, Redis cache)

        Args:
            db: Database session
            document_id: Document ID to delete
            vector_store: VectorStore instance (optional, for cleaning ChromaDB)
            cache_manager: CacheManager instance (optional, for cache invalidation)

        Returns:
            Tuple (success: bool, deleted_chunk_count: int)
        """
        doc = DocumentCRUD.get(db, document_id)
        if not doc:
            return False, 0

        try:
            # Get all chunks before deletion (for vector store cleanup)
            chunks = db.query(Chunk).filter(Chunk.document_id == document_id).all()
            chunk_ids = [c.chunk_id for c in chunks]
            chunk_count = len(chunks)

            # Delete from PostgreSQL (cascade deletes chunks)
            db.delete(doc)
            db.commit()
            logger.info(f"Deleted document {document_id} from PostgreSQL")

            # Delete embeddings from ChromaDB
            if vector_store and chunk_ids:
                for collection in vector_store.collections_names:
                    vector_store.delete_chunks(collection, chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} embeddings for document {document_id}")

            # Invalidate cache entries
            if cache_manager:
                cache_manager.invalidate_cache("query:*")
                logger.info(f"Invalidated query cache for document {document_id}")

            logger.info(f"Document {document_id} deleted from all storage systems")
            return True, chunk_count

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False, 0

    @staticmethod
    def count(db: Session, status: Optional[str] = None) -> int:
        """Count documents"""
        query = db.query(Document)
        if status:
            query = query.filter(Document.status == status)
        return query.count()


class ChunkCRUD:
    """CRUD operations for chunks"""

    @staticmethod
    def create(db: Session, chunk_id: str, document_id: str, content: str, chunk_type: str, token_count: int = 0):
        """Create a new chunk"""
        chunk = Chunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content=content,
            chunk_type=chunk_type,
            token_count=token_count
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def bulk_create(db: Session, chunks: List[dict]):
        """Create multiple chunks at once"""
        chunk_objects = []
        for chunk_data in chunks:
            chunk = Chunk(**chunk_data)
            chunk_objects.append(chunk)
        db.add_all(chunk_objects)
        db.commit()
        logger.info(f"Created {len(chunk_objects)} chunks")
        return chunk_objects

    @staticmethod
    def get(db: Session, chunk_id: str) -> Optional[Chunk]:
        """Get chunk by ID"""
        return db.query(Chunk).filter(Chunk.chunk_id == chunk_id).first()

    @staticmethod
    def get_by_document(db: Session, document_id: str, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get all chunks for a document"""
        return db.query(Chunk).filter(Chunk.document_id == document_id).offset(skip).limit(limit).all()

    @staticmethod
    def mark_indexed(db: Session, chunk_id: str):
        """Mark chunk as indexed"""
        chunk = ChunkCRUD.get(db, chunk_id)
        if chunk:
            chunk.is_indexed = True
            db.commit()
        return chunk

    @staticmethod
    def bulk_mark_indexed(db: Session, chunk_ids: List[str]):
        """Mark multiple chunks as indexed"""
        db.query(Chunk).filter(Chunk.chunk_id.in_(chunk_ids)).update({Chunk.is_indexed: True})
        db.commit()
        logger.info(f"Marked {len(chunk_ids)} chunks as indexed")

    @staticmethod
    def count_by_document(db: Session, document_id: str) -> int:
        """Count chunks for a document"""
        return db.query(Chunk).filter(Chunk.document_id == document_id).count()

    @staticmethod
    def delete_by_document(db: Session, document_id: str):
        """Delete all chunks for a document"""
        count = db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        db.commit()
        logger.info(f"Deleted {count} chunks for document {document_id}")
        return count


class ProcessingTaskCRUD:
    """CRUD operations for processing tasks"""

    @staticmethod
    def create(db: Session, task_id: str, document_id: str, task_type: str, celery_task_id: str = None):
        """Create a new processing task"""
        task = ProcessingTask(
            task_id=task_id,
            document_id=document_id,
            task_type=task_type,
            celery_task_id=celery_task_id,
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get(db: Session, task_id: str) -> Optional[ProcessingTask]:
        """Get task by ID"""
        return db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()

    @staticmethod
    def get_by_celery_id(db: Session, celery_task_id: str) -> Optional[ProcessingTask]:
        """Get task by Celery task ID"""
        return db.query(ProcessingTask).filter(ProcessingTask.celery_task_id == celery_task_id).first()

    @staticmethod
    def update_progress(db: Session, task_id: str, progress: int, current_step: str = None):
        """Update task progress"""
        task = ProcessingTaskCRUD.get(db, task_id)
        if task:
            task.progress = progress
            if current_step:
                task.current_step = current_step
            db.commit()
        return task

    @staticmethod
    def update_status(db: Session, task_id: str, status: str, error_message: str = None, result_data: str = None):
        """Update task status"""
        task = ProcessingTaskCRUD.get(db, task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()
            if status == "completed":
                task.completed_at = datetime.utcnow()
            if error_message:
                task.error_message = error_message
            if result_data:
                task.result_data = result_data
            db.commit()
        return task

    @staticmethod
    def get_by_document(db: Session, document_id: str) -> List[ProcessingTask]:
        """Get all tasks for a document"""
        return db.query(ProcessingTask).filter(ProcessingTask.document_id == document_id).order_by(ProcessingTask.created_at.desc()).all()


class QueryLogCRUD:
    """CRUD operations for query logs"""

    @staticmethod
    def create(db: Session, query_id: str, query_text: str):
        """Create a new query log"""
        log = QueryLog(
            query_id=query_id,
            query_text=query_text
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update(db: Session, query_id: str, response_text: str = None, chunks_retrieved: int = 0,
               chunks_reranked: int = 0, latency_ms: float = None):
        """Update query log with results"""
        log = db.query(QueryLog).filter(QueryLog.query_id == query_id).first()
        if log:
            log.response_text = response_text
            log.chunks_retrieved = chunks_retrieved
            log.chunks_reranked = chunks_reranked
            log.response_latency_ms = latency_ms
            db.commit()
        return log

    @staticmethod
    def add_feedback(db: Session, query_id: str, feedback: str):
        """Add user feedback to query"""
        log = db.query(QueryLog).filter(QueryLog.query_id == query_id).first()
        if log:
            log.user_feedback = feedback
            db.commit()
        return log

    @staticmethod
    def get_recent(db: Session, limit: int = 50) -> List[QueryLog]:
        """Get recent queries"""
        return db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """Count total queries"""
        return db.query(QueryLog).count()
