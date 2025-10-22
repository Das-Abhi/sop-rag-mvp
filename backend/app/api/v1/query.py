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
        query_text = request.query or request.query_text
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")

        logger.info(f"Processing query: {query_text[:50]}...")

        # Build system prompt with document context to help resolve pronouns
        system_prompt = request.system_prompt
        if not system_prompt:
            doc_context = ""
            if request.document_ids:
                doc_context = f" You are analyzing the following documents: {', '.join(request.document_ids)}."
            system_prompt = f"You are a helpful assistant. Answer the user's question based on the provided context. If a pronoun like 'he', 'she', 'they' is used, refer to the main person/subject in the documents.{doc_context} If the context doesn't contain relevant information, say so."

        # Call RAG engine
        rerank_top_k = request.rerank_top_k or request.top_k
        result = rag_engine.answer_query(
            query=query_text,
            top_k=request.top_k,
            rerank_top_k=rerank_top_k,
            system_prompt=system_prompt
        )

        logger.info(f"Query processed successfully, {len(result.get('citations', []))} sources")

        return QueryResponse(**result)

    except HTTPException:
        raise
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
        query_text = request.query or request.query_text
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")

        logger.info(f"Retrieving chunks for: {query_text[:50]}...")

        # Retrieve without generating response
        chunks = rag_engine.retrieve_relevant_chunks(
            query=query_text,
            top_k=request.top_k
        )

        # Rerank if requested
        rerank_top_k = request.rerank_top_k or request.top_k
        if rerank_top_k and rerank_top_k < len(chunks):
            chunks = rag_engine.rerank_results(
                query=query_text,
                chunks=chunks,
                top_k=rerank_top_k
            )

        logger.info(f"Retrieved {len(chunks)} chunks")

        return {
            "chunks": chunks,
            "count": len(chunks),
            "query": query_text
        }

    except HTTPException:
        raise
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
