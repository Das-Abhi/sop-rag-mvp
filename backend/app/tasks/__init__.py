"""
Celery tasks for background processing
"""
from .document_tasks import (
    process_document,
    generate_embeddings,
    index_chunks,
    cleanup_old_results
)

__all__ = [
    "process_document",
    "generate_embeddings",
    "index_chunks",
    "cleanup_old_results",
]
