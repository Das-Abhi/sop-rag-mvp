# Processing schemas
"""
Schemas for document processing status
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProcessingStatus(BaseModel):
    """Processing status information"""
    task_id: str
    document_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: int = Field(..., ge=0, le=100)
    current_step: str
    total_steps: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

class ProcessingUpdate(BaseModel):
    """Processing update broadcast"""
    task_id: str
    document_id: str
    progress: int
    status: str
    current_step: str
    message: Optional[str]

class ProcessingResult(BaseModel):
    """Final processing result"""
    document_id: str
    success: bool
    text_chunks: int
    image_chunks: int
    table_chunks: int
    composite_chunks: int
    processing_time_seconds: float
    error_message: Optional[str]
