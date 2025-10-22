"""
Query and RAG API endpoints
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from app.schemas import QueryRequest, QueryResponse, SearchResponse, SearchResult

router = APIRouter(prefix="/query", tags=["query"])

# Will be initialized by the main app
rag_engine = None


def set_rag_engine(engine):
    """Set the RAG engine instance"""
    global rag_engine
    rag_engine = engine


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Submit a RAG query

    Args:
        request: QueryRequest with query text and parameters

    Returns:
        QueryResponse with answer and citations
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    try:
        logger.info(f"Processing query: {request.query[:50]}...")

        # Call RAG engine
        result = rag_engine.answer_query(
            query=request.query,
            top_k=request.top_k,
            rerank_top_k=request.rerank_top_k,
            system_prompt=request.system_prompt
        )

        logger.info(f"Query processed successfully, {len(result.get('citations', []))} sources")

        return QueryResponse(**result)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/retrieve")
async def retrieve_chunks(request: QueryRequest):
    """
    Retrieve relevant chunks without generating response

    Args:
        request: QueryRequest with query text

    Returns:
        List of retrieved chunks with similarity scores
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    try:
        logger.info(f"Retrieving chunks for: {request.query[:50]}...")

        # Retrieve without generating response
        chunks = rag_engine.retrieve_relevant_chunks(
            query=request.query,
            top_k=request.top_k
        )

        # Rerank if requested
        if request.rerank_top_k < len(chunks):
            chunks = rag_engine.rerank_results(
                query=request.query,
                chunks=chunks,
                top_k=request.rerank_top_k
            )

        logger.info(f"Retrieved {len(chunks)} chunks")

        return {
            "chunks": chunks,
            "count": len(chunks),
            "query": request.query
        }

    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks: {str(e)}")


@router.get("/health")
async def query_health():
    """
    Check RAG engine health

    Returns:
        Health status
    """
    if not rag_engine:
        return {"status": "not_initialized"}

    try:
        # Try a simple test
        result = rag_engine.answer_query("test query")
        return {"status": "ok", "rag_available": True}
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {"status": "error", "message": str(e)}
