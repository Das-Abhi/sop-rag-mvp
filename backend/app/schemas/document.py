# Document schemas
"""
Pydantic schemas for document operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    """Create document request"""
    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    source: str = Field(..., description="Document source (upload/drive/dropbox)")

class DocumentUpdate(BaseModel):
    """Update document request"""
    title: Optional[str] = None
    description: Optional[str] = None

class DocumentInfo(BaseModel):
    """Document information"""
    document_id: str
    title: str
    description: Optional[str]
    file_path: str
    file_size: int
    page_count: int
    created_at: datetime
    updated_at: datetime
    status: str  # 'pending', 'processing', 'completed', 'failed'
    text_chunks: int
    image_chunks: int
    table_chunks: int

class DocumentListResponse(BaseModel):
    """Document list response"""
    documents: list[DocumentInfo]
    total: int
    page: int
    page_size: int
