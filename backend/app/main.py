# FastAPI application entry point
"""
Main FastAPI application for SOP RAG MVP
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os

# Import services
from app.services.vector_store import VectorStore
from app.core.cache_manager import CacheManager
from app.core.embedding_service import EmbeddingService
from app.core.llm_service import LLMService
from app.core.reranker import Reranker
from app.core.rag_engine import RAGEngine

# Import database
from app.database import init_db

# Import API routes
from app.api.v1 import query, documents, processing, websocket

app = FastAPI(
    title="SOP RAG MVP",
    description="Multimodal RAG system for SOP compliance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
vector_store = None
cache_manager = None
embedding_service = None
llm_service = None
reranker = None
rag_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, cache_manager, embedding_service, llm_service, reranker, rag_engine

    try:
        logger.info("Initializing SOP RAG MVP services...")

        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Initialize Vector Store
        chroma_path = os.getenv("CHROMA_PATH", "./data/chromadb")
        vector_store = VectorStore(chroma_path=chroma_path)
        logger.info("Vector Store initialized")

        # Initialize Cache Manager
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        cache_manager = CacheManager(redis_host=redis_host, redis_port=redis_port)
        logger.info("Cache Manager initialized")

        # Initialize Embedding Service
        embedding_service = EmbeddingService()
        logger.info("Embedding Service initialized")

        # Initialize LLM Service
        llm_service = LLMService()
        logger.info("LLM Service initialized")

        # Initialize Reranker
        reranker = Reranker()
        logger.info("Reranker initialized")

        # Initialize RAG Engine
        rag_engine = RAGEngine(
            vector_store=vector_store,
            embedding_service=embedding_service,
            llm_service=llm_service,
            reranker_service=reranker,
            cache_manager=cache_manager
        )
        logger.info("RAG Engine initialized")

        # Set service instances in API routes
        query.set_rag_engine(rag_engine)
        processing.set_services(vector_store, llm_service, embedding_service)

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SOP RAG MVP...")
    # Cleanup if needed
    logger.info("Shutdown complete")


# Include API routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(processing.router, prefix="/api/v1")
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SOP RAG MVP",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "services": {
            "vector_store": "initialized" if vector_store else "not_initialized",
            "cache": "initialized" if cache_manager else "not_initialized",
            "embeddings": "initialized" if embedding_service else "not_initialized",
            "llm": "initialized" if llm_service else "not_initialized",
            "rag": "initialized" if rag_engine else "not_initialized"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
