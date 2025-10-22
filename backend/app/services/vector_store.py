# Vector store wrapper
"""
ChromaDB vector store integration for storing and retrieving document chunks
"""
from typing import List, Dict, Optional
import chromadb
from loguru import logger
import os


class VectorStore:
    """ChromaDB wrapper for vector storage and retrieval"""

    def __init__(self, chroma_path: str = "./data/chromadb"):
        """
        Initialize ChromaDB vector store

        Args:
            chroma_path: Path to ChromaDB persistent storage
        """
        self.chroma_path = chroma_path
        self.collections_names = ["text_chunks", "image_chunks", "table_chunks", "composite_chunks"]

        # Create directory if it doesn't exist
        os.makedirs(chroma_path, exist_ok=True)

        # Initialize ChromaDB client with persistent storage (new API)
        try:
            self.client = chromadb.PersistentClient(path=chroma_path)
        except Exception:
            # Fallback for older ChromaDB versions
            self.client = chromadb.Client()

        self.collections = {}

        # Initialize all collections
        self._initialize_collections()
        logger.info(f"VectorStore initialized at {chroma_path}")

    def _initialize_collections(self):
        """Initialize or get reference to all collections"""
        for collection_name in self.collections_names:
            try:
                self.collections[collection_name] = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.debug(f"Collection '{collection_name}' ready")
            except Exception as e:
                logger.error(f"Error initializing collection '{collection_name}': {e}")
                raise

    def add_chunks(self, collection: str, chunks: List[Dict]) -> bool:
        """
        Add chunks to collection

        Args:
            collection: Collection name (text_chunks, image_chunks, etc.)
            chunks: List of chunk dictionaries with id, embedding, content, metadata

        Returns:
            True if successful, False otherwise
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return False

        if not chunks:
            logger.warning("No chunks provided to add")
            return True

        try:
            # Prepare data for ChromaDB
            ids = [chunk.get("id") or chunk.get("chunk_id") for chunk in chunks]
            embeddings = [chunk.get("embedding") for chunk in chunks]
            metadatas = [chunk.get("metadata", {}) for chunk in chunks]
            documents = [chunk.get("content") for chunk in chunks]

            # Add to collection
            self.collections[collection].add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"Added {len(chunks)} chunks to '{collection}'")
            return True
        except Exception as e:
            logger.error(f"Error adding chunks to '{collection}': {e}")
            return False

    def search(
        self,
        collection: str,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Search for similar chunks

        Args:
            collection: Collection name to search in
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            filters: Optional metadata filters

        Returns:
            List of search results with similarity scores
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return []

        try:
            results = self.collections[collection].query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters if filters else None
            )

            # Format results
            formatted_results = []
            if results and results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 1.0,
                        # Convert distance to similarity (cosine distance to similarity)
                        "similarity": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })

            logger.debug(f"Found {len(formatted_results)} similar chunks in '{collection}'")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching collection '{collection}': {e}")
            return []

    def delete_chunks(self, collection: str, chunk_ids: List[str]) -> bool:
        """
        Delete chunks from collection

        Args:
            collection: Collection name
            chunk_ids: List of chunk IDs to delete

        Returns:
            True if successful, False otherwise
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return False

        if not chunk_ids:
            logger.warning("No chunk IDs provided to delete")
            return True

        try:
            self.collections[collection].delete(ids=chunk_ids)
            logger.info(f"Deleted {len(chunk_ids)} chunks from '{collection}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting chunks from '{collection}': {e}")
            return False

    def update_chunks(self, collection: str, chunks: List[Dict]) -> bool:
        """
        Update existing chunks

        Args:
            collection: Collection name
            chunks: List of chunk dictionaries with updated data

        Returns:
            True if successful, False otherwise
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return False

        if not chunks:
            logger.warning("No chunks provided to update")
            return True

        try:
            # Extract IDs first to delete old chunks
            ids = [chunk.get("id") or chunk.get("chunk_id") for chunk in chunks]

            # Delete old chunks
            self.collections[collection].delete(ids=ids)

            # Add updated chunks
            return self.add_chunks(collection, chunks)
        except Exception as e:
            logger.error(f"Error updating chunks in '{collection}': {e}")
            return False

    def get_collection_stats(self, collection: str) -> Dict:
        """
        Get collection statistics

        Args:
            collection: Collection name

        Returns:
            Dictionary with collection stats
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return {}

        try:
            count = self.collections[collection].count()
            return {
                "name": collection,
                "count": count,
                "status": "ok"
            }
        except Exception as e:
            logger.error(f"Error getting stats for '{collection}': {e}")
            return {"name": collection, "count": 0, "status": "error"}

    def clear_collection(self, collection: str) -> bool:
        """
        Clear entire collection

        Args:
            collection: Collection name

        Returns:
            True if successful, False otherwise
        """
        if collection not in self.collections:
            logger.error(f"Collection '{collection}' does not exist")
            return False

        try:
            # Delete and recreate collection
            self.client.delete_collection(name=collection)
            self.collections[collection] = self.client.get_or_create_collection(
                name=collection,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection '{collection}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection '{collection}': {e}")
            return False

    def get_all_stats(self) -> Dict:
        """
        Get statistics for all collections

        Returns:
            Dictionary with stats for each collection
        """
        stats = {}
        for collection in self.collections_names:
            stats[collection] = self.get_collection_stats(collection)
        return stats
