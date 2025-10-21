# Document model
"""
SQLAlchemy document model
"""
from datetime import datetime

class DocumentModel:
    """Document database model"""
    # TODO: Implement SQLAlchemy model with columns:
    # - id (primary key)
    # - title
    # - description
    # - file_path
    # - file_size
    # - file_hash
    # - page_count
    # - status
    # - processing_started_at
    # - processing_completed_at
    # - created_at
    # - updated_at
    # - source (upload/drive/dropbox)
    pass

class ChunkModel:
    """Chunk database model"""
    # TODO: Implement SQLAlchemy model with columns:
    # - id (primary key)
    # - document_id (foreign key)
    # - chunk_type (text/image/table/composite)
    # - content
    # - embedding (vector)
    # - metadata (jsonb)
    # - created_at
    pass

class ImageModel:
    """Image database model"""
    # TODO: Implement SQLAlchemy model with columns:
    # - id (primary key)
    # - document_id (foreign key)
    # - object_id (MinIO reference)
    # - description (AI-generated)
    # - embedding (visual features)
    # - metadata
    # - created_at
    pass

class TableModel:
    """Table database model"""
    # TODO: Implement SQLAlchemy model with columns:
    # - id (primary key)
    # - document_id (foreign key)
    # - page_number
    # - table_data (jsonb)
    # - extraction_method
    # - confidence
    # - created_at
    pass
