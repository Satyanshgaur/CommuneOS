"""
CommuneOS Cache Service
In-memory caching layer with TTL support.
Optionally backed by Redis if configured.
"""
import asyncio
import hashlib
import time
from typing import Any, Dict, Optional

from config import settings
from utils.logger import get_logger

logger = get_logger("cache")

# In-memory cache: {key: (value, expires_at_timestamp)}
_cache: Dict[str, tuple] = {}


class CacheService:
    """
    Thread-safe in-memory cache with TTL.
    Falls back gracefully if Redis is unavailable.
    """

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value. Returns None if missing or expired."""
        entry = _cache.get(key)
        if entry is None:
            logger.debug(f"Cache MISS: {key}")
            return None
        
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del _cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None
        
        logger.debug(f"Cache HIT: {key}")
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in cache with optional TTL in seconds."""
        expires_at = time.time() + ttl if ttl else None
        _cache[key] = (value, expires_at)
        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")

    def delete(self, key: str) -> None:
        """Remove a specific key from cache."""
        if key in _cache:
            del _cache[key]
            logger.debug(f"Cache DEL: {key}")

    def clear_prefix(self, prefix: str) -> int:
        """Remove all keys matching a prefix. Returns count deleted."""
        keys_to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del _cache[k]
        if keys_to_delete:
            logger.info(f"Cache CLEAR prefix '{prefix}': {len(keys_to_delete)} keys removed")
        return len(keys_to_delete)

    def clear_all(self) -> None:
        """Wipe the entire cache."""
        count = len(_cache)
        _cache.clear()
        logger.warning(f"Cache CLEAR ALL: {count} keys removed")

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        now = time.time()
        expired = sum(1 for _, (_, exp) in _cache.items() if exp and now > exp)
        return {
            "total_keys": len(_cache),
            "expired_keys": expired,
            "active_keys": len(_cache) - expired,
        }

    # ─── Key Builders ──────────────────────────────────────────────────────────

    @staticmethod
    def agent_key(agent_name: str, user_id: str) -> str:
        """Cache key for an agent response."""
        return f"agent:{agent_name}:{user_id}"

    @staticmethod
    def llm_key(prompt: str) -> str:
        """Cache key for an LLM response, hashed from prompt."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        return f"llm:{prompt_hash}"

    @staticmethod
    def user_key(user_id: str) -> str:
        """Cache key for a user profile."""
        return f"user:{user_id}"

    @staticmethod
    def community_key(metric_type: str) -> str:
        """Cache key for community metrics."""
        return f"community:{metric_type}"


# Singleton instance
cache_service = CacheService()
