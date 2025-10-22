# RAG engine
"""
Retrieval-Augmented Generation orchestration
"""
from typing import List, Dict, Tuple, Optional
from loguru import logger
import hashlib


class RAGEngine:
    """Main RAG orchestration engine"""

    def __init__(
        self,
        vector_store,
        embedding_service,
        llm_service,
        reranker_service,
        cache_manager
    ):
        """
        Initialize RAG Engine

        Args:
            vector_store: VectorStore instance for chunk retrieval
            embedding_service: EmbeddingService for query embeddings
            llm_service: LLMService for response generation
            reranker_service: RerankerService for result ranking
            cache_manager: CacheManager for caching
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.reranker_service = reranker_service
        self.cache_manager = cache_manager
        logger.info("RAG Engine initialized")

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict = None,
        collections: List[str] = None
    ) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query across multiple collections

        Args:
            query: Query text
            top_k: Number of top results to return per collection
            filters: Optional metadata filters
            collections: List of collections to search (default: all)

        Returns:
            List of retrieved chunks with similarity scores
        """
        try:
            if collections is None:
                collections = ["text_chunks", "image_chunks", "table_chunks", "composite_chunks"]

            # Check cache first
            cached_results = self.cache_manager.get_cached_query_result(query)
            if cached_results:
                logger.debug(f"Retrieved cached results for query")
                return cached_results

            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []

            # Search across collections
            all_results = []
            for collection in collections:
                try:
                    results = self.vector_store.search(
                        collection=collection,
                        query_embedding=query_embedding,
                        top_k=top_k,
                        filters=filters
                    )
                    # Add collection info to results
                    for result in results:
                        result["source_collection"] = collection
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"Error searching collection '{collection}': {e}")

            # Sort by similarity score
            all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            all_results = all_results[:top_k * len(collections)]

            logger.info(f"Retrieved {len(all_results)} chunks for query")
            return all_results

        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []

    def rerank_results(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rerank retrieved chunks using reranker model

        Args:
            query: Query text
            chunks: List of retrieved chunks
            top_k: Number of top results to return after reranking

        Returns:
            Reranked list of chunks
        """
        try:
            if not chunks:
                logger.warning("No chunks to rerank")
                return []

            # Use reranker if available
            if self.reranker_service:
                reranked_chunks = self.reranker_service.rerank(
                    query=query,
                    chunks=chunks,
                    top_k=top_k
                )
                logger.info(f"Reranked {len(chunks)} chunks to top {len(reranked_chunks)}")
                return reranked_chunks
            else:
                # Fallback: return top-k by similarity
                logger.debug("No reranker available, using similarity scores")
                return chunks[:top_k]

        except Exception as e:
            logger.error(f"Error reranking results: {e}")
            return chunks[:top_k]

    def generate_response(
        self,
        query: str,
        context_chunks: List[Dict],
        system_prompt: str = None
    ) -> Tuple[str, List[Dict]]:
        """
        Generate response using LLM with retrieved context

        Args:
            query: Query text
            context_chunks: Retrieved context chunks
            system_prompt: Optional system prompt

        Returns:
            Tuple of (response text, source chunks)
        """
        try:
            if not context_chunks:
                logger.warning("No context chunks provided for response generation")
                return "", []

            # Build context window
            context_text = self._build_context_window(context_chunks)

            # Prepare prompt
            if system_prompt is None:
                system_prompt = "You are a helpful assistant. Answer the user's question based on the provided context. If the context doesn't contain relevant information, say so."

            full_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nQuestion: {query}"

            # Generate response
            response = self.llm_service.generate(full_prompt)
            logger.info(f"Generated response for query")

            return response, context_chunks

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "", []

    def generate_with_citations(
        self,
        query: str,
        context_chunks: List[Dict],
        system_prompt: str = None
    ) -> Dict:
        """
        Generate response with source citations

        Args:
            query: Query text
            context_chunks: Retrieved context chunks
            system_prompt: Optional system prompt

        Returns:
            Dictionary with response and citations
        """
        try:
            response, sources = self.generate_response(query, context_chunks, system_prompt)

            # Extract citations
            citations = self._extract_citations(sources)

            result = {
                "response": response,
                "citations": citations,
                "num_sources": len(sources)
            }

            logger.info(f"Generated response with {len(citations)} citations")
            return result

        except Exception as e:
            logger.error(f"Error generating response with citations: {e}")
            return {
                "response": "",
                "citations": [],
                "num_sources": 0
            }

    def answer_query(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 5,
        system_prompt: str = None
    ) -> Dict:
        """
        End-to-end query answering pipeline

        Args:
            query: Query text
            top_k: Number of chunks to retrieve
            rerank_top_k: Number of chunks to use for response
            system_prompt: Optional system prompt

        Returns:
            Dictionary with complete response, citations, and metadata
        """
        try:
            logger.info(f"Starting query answering pipeline for: {query[:50]}...")

            # Step 1: Retrieve relevant chunks
            retrieved_chunks = self.retrieve_relevant_chunks(query, top_k=top_k)
            if not retrieved_chunks:
                logger.warning("No chunks retrieved for query")
                return {
                    "response": "I couldn't find relevant information to answer your question.",
                    "citations": [],
                    "num_sources": 0,
                    "metadata": {
                        "retrieved_chunks": 0,
                        "reranked_chunks": 0,
                        "processing_time": 0
                    }
                }

            # Step 2: Rerank results
            reranked_chunks = self.rerank_results(query, retrieved_chunks, rerank_top_k)

            # Step 3: Generate response with citations
            result = self.generate_with_citations(query, reranked_chunks, system_prompt)

            # Add metadata
            result["metadata"] = {
                "retrieved_chunks": len(retrieved_chunks),
                "reranked_chunks": len(reranked_chunks),
                "query_length": len(query)
            }

            logger.info(f"Completed query answering pipeline")
            return result

        except Exception as e:
            logger.error(f"Error in query answering pipeline: {e}")
            return {
                "response": f"Error: {str(e)}",
                "citations": [],
                "num_sources": 0,
                "metadata": {}
            }

    def _build_context_window(self, chunks: List[Dict], max_chars: int = 4000) -> str:
        """
        Build context window from chunks

        Args:
            chunks: List of chunks
            max_chars: Maximum characters for context

        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0

        for i, chunk in enumerate(chunks):
            content = chunk.get("content", "")
            source = chunk.get("metadata", {}).get("source_file", "unknown")

            chunk_text = f"[Source {i+1}: {source}]\n{content}"

            if current_length + len(chunk_text) > max_chars:
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        return "\n\n".join(context_parts)

    def _extract_citations(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract citations from source chunks

        Args:
            chunks: Source chunks

        Returns:
            List of citations
        """
        citations = []
        for i, chunk in enumerate(chunks):
            citation = {
                "index": i + 1,
                "source": chunk.get("metadata", {}).get("source_file", "unknown"),
                "page": chunk.get("metadata", {}).get("page_num", None),
                "content_preview": chunk.get("content", "")[:200]
            }
            citations.append(citation)

        return citations
