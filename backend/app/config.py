# Configuration management
"""
Configuration settings for the SOP RAG MVP application
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration"""

    # App settings
    APP_NAME: str = "SOP RAG MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/sop_rag"
    SQLALCHEMY_ECHO: bool = False

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MinIO settings
    MINIO_HOST: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "sop-rag"

    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TEXT_MODEL: str = "llama3.1:8b"
    OLLAMA_VISION_MODEL: str = "bakllava:7b"
    OLLAMA_FALLBACK_MODEL: str = "mistral:7b"

    # Embedding settings
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    IMAGE_EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"

    # ChromaDB settings
    CHROMA_PATH: str = "./data/chromadb"

    # Document processing settings
    MAX_UPLOAD_SIZE_MB: int = 500
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Google Drive settings
    GOOGLE_DRIVE_CREDENTIALS: Optional[str] = None
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None

    # Dropbox settings
    DROPBOX_ACCESS_TOKEN: Optional[str] = None

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
