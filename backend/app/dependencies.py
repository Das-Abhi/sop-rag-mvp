# FastAPI dependencies
"""
FastAPI dependency injection utilities
"""
from typing import Generator
from app.config import settings

def get_settings():
    """Get application settings"""
    return settings

def get_db_session():
    """Get database session"""
    # Placeholder for database session dependency
    # Will be implemented in db/session.py
    pass

def get_redis_client():
    """Get Redis client"""
    # Placeholder for Redis client dependency
    pass

def get_vector_store():
    """Get vector store client"""
    # Placeholder for ChromaDB client dependency
    pass
