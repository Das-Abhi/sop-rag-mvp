"""
Document management API endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import uuid
from datetime import datetime
from loguru import logger
import os
import shutil

from app.schemas import DocumentInfo, DocumentListResponse, DocumentCreate
from app.celery_app import app as celery_app
from app.tasks.document_tasks import process_document
from app.database import SessionLocal
from app.crud import DocumentCRUD

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing

    Args:
        file: PDF file to upload

    Returns:
        DocumentInfo with document ID and status
    """
    try:
        # Generate document ID
        document_id = str(uuid.uuid4())

        # Validate file
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Supported: PDF, DOCX, TXT")

        if file.size and file.size > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(status_code=400, detail="File too large (max 100MB)")

        # Create document directory
        doc_dir = f"./data/uploads/{document_id}"
        os.makedirs(doc_dir, exist_ok=True)

        # Save file
        file_path = f"{doc_dir}/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Determine document type
        doc_type = "pdf" if file.content_type == "application/pdf" else "txt"

        # Store in database
        db = SessionLocal()
        doc_data = None
        try:
            doc = DocumentCRUD.create(
                db=db,
                document_id=document_id,
                title=file.filename or "Untitled",
                file_path=file_path,
                file_size=len(content),
                file_type=doc_type
            )
            db.commit()
            # Extract data while session is still open
            doc_data = DocumentInfo(
                document_id=doc.document_id,
                title=doc.title,
                description=doc.description,
                file_path=doc.file_path,
                file_size=doc.file_size,
                page_count=doc.page_count,
                status=doc.status,
                text_chunks=doc.text_chunks,
                image_chunks=doc.image_chunks,
                table_chunks=doc.table_chunks,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
        finally:
            db.close()

        # Queue background task
        task = process_document.delay(document_id, file_path, doc_type)
        logger.info(f"Document uploaded: {document_id}, task: {task.id}")

        return doc_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str):
    """
    Get document status and metadata

    Args:
        document_id: Document ID

    Returns:
        DocumentInfo with current status
    """
    db = SessionLocal()
    try:
        doc = DocumentCRUD.get(db, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_data = DocumentInfo(
            document_id=doc.document_id,
            title=doc.title,
            description=doc.description,
            file_path=doc.file_path,
            file_size=doc.file_size,
            page_count=doc.page_count,
            status=doc.status,
            text_chunks=doc.text_chunks,
            image_chunks=doc.image_chunks,
            table_chunks=doc.table_chunks,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
        return doc_data
    finally:
        db.close()


@router.get("", response_model=DocumentListResponse)
async def list_documents(status: str = None, page: int = 1, page_size: int = 10):
    """
    List all documents

    Args:
        status: Optional filter by status (pending, processing, completed, error)
        page: Page number
        page_size: Items per page

    Returns:
        DocumentListResponse with documents
    """
    db = SessionLocal()
    try:
        docs = DocumentCRUD.list_all(db)

        if status:
            docs = [d for d in docs if d.status == status]

        total = len(docs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_docs = docs[start:end]

        # Extract data while session is still open
        documents = [
            DocumentInfo(
                document_id=doc.document_id,
                title=doc.title,
                description=doc.description,
                file_path=doc.file_path,
                file_size=doc.file_size,
                page_count=doc.page_count,
                status=doc.status,
                text_chunks=doc.text_chunks,
                image_chunks=doc.image_chunks,
                table_chunks=doc.table_chunks,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in paginated_docs
        ]

        return DocumentListResponse(
            documents=documents,
            total=total,
            page=page,
            page_size=page_size
        )
    finally:
        db.close()


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document

    Args:
        document_id: Document ID

    Returns:
        Success message
    """
    db = SessionLocal()
    try:
        doc = DocumentCRUD.get(db, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        DocumentCRUD.delete(db, document_id)
        db.commit()
        logger.info(f"Document deleted: {document_id}")

        return {"message": "Document deleted successfully", "document_id": document_id}
    finally:
        db.close()


@router.put("/{document_id}/status")
async def update_document_status(document_id: str, status: str):
    """
    Update document processing status

    Args:
        document_id: Document ID
        status: New status (pending, processing, completed, error)

    Returns:
        Updated DocumentInfo
    """
    db = SessionLocal()
    try:
        doc = DocumentCRUD.get(db, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if status not in ["pending", "processing", "completed", "error"]:
            raise HTTPException(status_code=400, detail="Invalid status")

        updated_doc = DocumentCRUD.update_status(db, document_id, status)
        db.commit()
        logger.info(f"Document {document_id} status updated to: {status}")

        # Extract data while session is still open
        doc_data = DocumentInfo(
            document_id=updated_doc.document_id,
            title=updated_doc.title,
            description=updated_doc.description,
            file_path=updated_doc.file_path,
            file_size=updated_doc.file_size,
            page_count=updated_doc.page_count,
            status=updated_doc.status,
            text_chunks=updated_doc.text_chunks,
            image_chunks=updated_doc.image_chunks,
            table_chunks=updated_doc.table_chunks,
            created_at=updated_doc.created_at,
            updated_at=updated_doc.updated_at
        )
        return doc_data
    finally:
        db.close()
