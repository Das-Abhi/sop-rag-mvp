"""
Document processing status and monitoring endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from loguru import logger

from app.schemas import ProcessingStatus

router = APIRouter(prefix="/processing", tags=["processing"])

# Will be initialized by the main app
vector_store = None
llm_service = None
embedding_service = None


def set_services(vs, llm, embed):
    """Set service instances"""
    global vector_store, llm_service, embedding_service
    vector_store = vs
    llm_service = llm
    embedding_service = embed


@router.get("/status/{document_id}", response_model=ProcessingStatus)
async def get_processing_status(document_id: str):
    """
    Get document processing status

    Args:
        document_id: Document ID

    Returns:
        ProcessingStatus with current progress
    """
    try:
        # In a real implementation, this would query the database/task queue
        # For now, return a sample response
        from datetime import datetime
        return ProcessingStatus(
            task_id=f"task-{document_id}",
            document_id=document_id,
            status="completed",
            progress=100,
            current_step="completed",
            total_steps=5,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            error_message=None
        )
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.get("/vector-store-stats")
async def get_vector_store_stats():
    """
    Get vector store statistics

    Returns:
        Statistics for each collection
    """
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        stats = vector_store.get_all_stats()
        logger.debug("Retrieved vector store statistics")
        return stats
    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/collection-stats/{collection}")
async def get_collection_stats(collection: str):
    """
    Get statistics for a specific collection

    Args:
        collection: Collection name (text_chunks, image_chunks, table_chunks, composite_chunks)

    Returns:
        Collection statistics
    """
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        stats = vector_store.get_collection_stats(collection)
        if not stats or "status" not in stats:
            raise HTTPException(status_code=404, detail=f"Collection '{collection}' not found")

        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/health")
async def get_system_health():
    """
    Get overall system health

    Returns:
        System health status with service information
    """
    try:
        services = {
            "vector_store": "ok" if vector_store else "not_initialized",
            "llm": "ok" if llm_service else "not_initialized",
            "embeddings": "ok" if embedding_service else "not_initialized"
        }

        # Check LLM health
        if llm_service:
            try:
                models = llm_service.list_available_models()
                services["llm"] = "ok" if models else "no_models"
            except:
                services["llm"] = "error"

        # Get vector store stats
        vector_store_stats = {}
        if vector_store:
            try:
                all_stats = vector_store.get_all_stats()
                vector_store_stats = {name: stats.get("count", 0) for name, stats in all_stats.items()}
            except:
                pass

        # Get available models
        available_models = []
        if llm_service:
            try:
                available_models = llm_service.list_available_models()
            except:
                available_models = []

        overall_status = "ok" if all(s == "ok" for s in services.values()) else "degraded"

        logger.debug("System health check completed")

        return {
            "status": overall_status,
            "services": services,
            "vector_store": vector_store_stats,
            "models_available": available_models
        }

    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {
            "status": "error",
            "services": {},
            "vector_store": {},
            "models_available": []
        }


@router.post("/clear-cache")
async def clear_cache():
    """
    Clear all caches (Redis, etc.)

    Returns:
        Success message
    """
    try:
        # In a real implementation, this would clear Redis cache
        logger.info("Cache cleared")
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")
