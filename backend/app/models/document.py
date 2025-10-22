# Document model
"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    """Document metadata model"""
    __tablename__ = "documents"

    document_id = Column(String(36), primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    page_count = Column(Integer, default=0)
    status = Column(String(20), default="pending", index=True)
    text_chunks = Column(Integer, default=0)
    image_chunks = Column(Integer, default=0)
    table_chunks = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    celery_task_id = Column(String(36), nullable=True)

    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """Document chunk model"""
    __tablename__ = "chunks"

    chunk_id = Column(String(128), primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), index=True)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(20), nullable=False)
    token_count = Column(Integer, default=0)
    embedding_vector = Column(String, nullable=True)
    similarity_score = Column(Float, nullable=True)
    page_num = Column(Integer, nullable=True)
    section = Column(String(256), nullable=True)
    source_file = Column(String(256), nullable=True)
    is_indexed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class ProcessingTask(Base):
    """Background task tracking model"""
    __tablename__ = "processing_tasks"

    task_id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), index=True)
    celery_task_id = Column(String(36), nullable=True, index=True)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending", index=True)
    progress = Column(Integer, default=0)
    current_step = Column(String(256), nullable=True)
    total_steps = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QueryLog(Base):
    """Query history and analytics model"""
    __tablename__ = "query_logs"

    query_id = Column(String(36), primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    document_ids_used = Column(String, nullable=True)
    chunks_retrieved = Column(Integer, default=0)
    chunks_reranked = Column(Integer, default=0)
    response_latency_ms = Column(Float, nullable=True)
    user_feedback = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
