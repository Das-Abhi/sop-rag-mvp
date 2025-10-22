# Cache manager
"""
Redis-based caching for embeddings, queries, and results
"""
from typing import Optional, Any, List
import redis
import json
import hashlib
from loguru import logger


class CacheManager:
    """Manages caching with Redis"""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize Redis cache manager

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.default_ttl = 3600  # 1 hour

        # Connect to Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _get_key(self, prefix: str, value: str) -> str:
        """Generate cache key with prefix and hash"""
        value_hash = hashlib.md5(value.encode()).hexdigest()
        return f"{prefix}:{value_hash}"

    def cache_embedding(self, text: str, embedding: List[float], ttl: int = None) -> bool:
        """
        Cache text embedding

        Args:
            text: Original text
            embedding: Embedding vector
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._get_key("embedding", text)
            ttl = ttl or self.default_ttl

            # Store as JSON
            self.redis_client.setex(key, ttl, json.dumps(embedding))
            logger.debug(f"Cached embedding for text: {key}")
            return True
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
            return False

    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """
        Retrieve cached embedding

        Args:
            text: Original text

        Returns:
            Embedding vector or None if not found
        """
        try:
            key = self._get_key("embedding", text)
            cached_value = self.redis_client.get(key)

            if cached_value:
                logger.debug(f"Retrieved cached embedding: {key}")
                return json.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached embedding: {e}")
            return None

    def cache_query_result(self, query: str, result: dict, ttl: int = None) -> bool:
        """
        Cache query result

        Args:
            query: Query text
            result: Query result dictionary
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._get_key("query", query)
            ttl = ttl or self.default_ttl

            # Store as JSON
            self.redis_client.setex(key, ttl, json.dumps(result, default=str))
            logger.debug(f"Cached query result: {key}")
            return True
        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return False

    def get_cached_query_result(self, query: str) -> Optional[dict]:
        """
        Retrieve cached query result

        Args:
            query: Query text

        Returns:
            Query result dictionary or None if not found
        """
        try:
            key = self._get_key("query", query)
            cached_value = self.redis_client.get(key)

            if cached_value:
                logger.debug(f"Retrieved cached query result: {key}")
                return json.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached query result: {e}")
            return None

    def invalidate_cache(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern

        Args:
            pattern: Redis key pattern (e.g., "embedding:*", "query:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries for pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating cache with pattern '{pattern}': {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear entire cache

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis_client.flushdb()
            logger.info("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        try:
            info = self.redis_client.info()
            stats = {
                "used_memory": info.get("used_memory_human", "N/A"),
                "used_memory_peak": info.get("used_memory_peak_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace": {}
            }

            # Get database-specific stats
            db_key = f"db{self.redis_db}"
            if db_key in info:
                db_info = info[db_key]
                stats["keyspace"] = db_info

            logger.debug("Retrieved cache statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}
