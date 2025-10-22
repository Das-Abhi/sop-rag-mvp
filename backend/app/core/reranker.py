# Reranker module
"""
Result reranking using cross-encoder model for improved relevance
"""
from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
from loguru import logger


class Reranker:
    """Reranks search results for improved relevance using cross-encoder"""

    def __init__(self, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize Reranker with cross-encoder model

        Args:
            model: Model name for reranking (default: MiniLM cross-encoder for faster inference)
        """
        self.model_name = model
        try:
            # Load cross-encoder model
            self.model = CrossEncoder(model)
            logger.info(f"Reranker initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to load reranker model: {e}")
            self.model = None

    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Rerank candidates based on relevance to query

        Args:
            query: Query text
            chunks: List of chunk dictionaries with 'content' field
            top_k: Number of top results to return
            threshold: Minimum score threshold

        Returns:
            Reranked list of chunks with scores
        """
        if not self.model:
            logger.warning("Reranker model not available, returning original order")
            return chunks[:top_k]

        if not chunks:
            logger.warning("No chunks to rerank")
            return []

        try:
            # Extract texts for reranking
            texts = [chunk.get("content", "") for chunk in chunks]

            # Compute scores using cross-encoder
            scores = self.model.predict([[query, text] for text in texts])

            # Create list of (score, chunk) pairs
            scored_chunks = []
            for i, chunk in enumerate(chunks):
                chunk["relevance_score"] = float(scores[i])
                scored_chunks.append(chunk)

            # Sort by relevance score
            scored_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            # Filter by threshold
            filtered_chunks = [c for c in scored_chunks if c.get("relevance_score", 0) >= threshold]

            # Return top-k
            reranked = filtered_chunks[:top_k]
            logger.info(f"Reranked {len(chunks)} chunks, returned {len(reranked)} above threshold {threshold}")

            return reranked

        except Exception as e:
            logger.error(f"Error reranking results: {e}")
            # Fallback: return original top-k
            return chunks[:top_k]

    def compute_relevance_score(self, query: str, text: str) -> float:
        """
        Compute relevance score between query and text

        Args:
            query: Query text
            text: Document text

        Returns:
            Relevance score (0-1 approximately)
        """
        if not self.model:
            logger.warning("Reranker model not available")
            return 0.0

        try:
            score = self.model.predict([[query, text]])
            logger.debug(f"Computed relevance score: {score[0]:.4f}")
            return float(score[0])
        except Exception as e:
            logger.error(f"Error computing relevance score: {e}")
            return 0.0

    def filter_low_scores(
        self,
        results: List[Dict],
        threshold: float = 0.3
    ) -> List[Dict]:
        """
        Filter results below score threshold

        Args:
            results: List of results with 'relevance_score' field
            threshold: Minimum score to keep

        Returns:
            Filtered list of results
        """
        try:
            filtered = [r for r in results if r.get("relevance_score", 0) >= threshold]
            logger.info(f"Filtered {len(results)} results, keeping {len(filtered)} above {threshold}")
            return filtered
        except Exception as e:
            logger.error(f"Error filtering results: {e}")
            return results

    def group_similar_results(
        self,
        results: List[Dict],
        similarity_threshold: float = 0.8
    ) -> List[List[Dict]]:
        """
        Group similar results together based on score proximity

        Args:
            results: List of results with 'relevance_score' field
            similarity_threshold: Score difference threshold for grouping

        Returns:
            List of grouped results
        """
        if not results:
            return []

        try:
            groups = []
            current_group = [results[0]]
            current_score = results[0].get("relevance_score", 0)

            for result in results[1:]:
                score = result.get("relevance_score", 0)
                # Check if score is within threshold of current group
                if abs(score - current_score) <= (1 - similarity_threshold):
                    current_group.append(result)
                else:
                    groups.append(current_group)
                    current_group = [result]
                    current_score = score

            # Add final group
            if current_group:
                groups.append(current_group)

            logger.info(f"Grouped {len(results)} results into {len(groups)} groups")
            return groups

        except Exception as e:
            logger.error(f"Error grouping results: {e}")
            return [results]
