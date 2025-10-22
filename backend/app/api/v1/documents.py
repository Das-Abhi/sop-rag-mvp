"""
Document management API endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import uuid
from datetime import datetime
from loguru import logger

from app.schemas import DocumentInfo, DocumentListResponse, DocumentCreate

router = APIRouter(prefix="/documents", tags=["documents"])


# In-memory storage for demo (replace with database in production)
documents_db = {}


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

        # Store document metadata
        doc_metadata = {
            "document_id": document_id,
            "title": file.filename or "Untitled",
            "description": None,
            "file_path": f"/tmp/{document_id}/{file.filename}",
            "file_size": file.size or 0,
            "page_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "pending",
            "text_chunks": 0,
            "image_chunks": 0,
            "table_chunks": 0
        }
        documents_db[document_id] = doc_metadata

        logger.info(f"Document uploaded: {document_id} ({file.filename})")

        return DocumentInfo(**doc_metadata)

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
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = documents_db[document_id]
    return DocumentInfo(**doc)


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
    docs = list(documents_db.values())

    if status:
        docs = [d for d in docs if d.get("status") == status]

    total = len(docs)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_docs = docs[start:end]

    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in paginated_docs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document

    Args:
        document_id: Document ID

    Returns:
        Success message
    """
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    del documents_db[document_id]
    logger.info(f"Document deleted: {document_id}")

    return {"message": "Document deleted successfully", "document_id": document_id}


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
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    if status not in ["pending", "processing", "completed", "error"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    documents_db[document_id]["status"] = status
    documents_db[document_id]["updated_at"] = datetime.utcnow()
    logger.info(f"Document {document_id} status updated to: {status}")

    return DocumentInfo(**documents_db[document_id])
