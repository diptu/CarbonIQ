# ima_service/app/utils/cache.py
"""Cache backend abstraction for RBAC role lookups."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Protocol, cast

from ima_service.app.core.config import get_settings

settings = get_settings()


class CacheBackend(Protocol):
    """Protocol for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache if it exists."""

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store a value in the cache with a time-to-live in seconds."""

    def delete(self, key: str) -> None:
        """Remove a value from the cache."""


class InMemoryCache:
    """In-memory cache using a dictionary with TTL."""

    def __init__(self) -> None:
        self._store: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if not expired."""
        item = self._store.get(key)
        if item is None:
            return None
        value, expires_at = item
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set a value with expiry."""
        self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        self._store.pop(key, None)


class RedisCache:
    """Redis cache wrapper (optional, requires redis-py)."""

    def __init__(self, url: str) -> None:
        try:
            import redis  # type: ignore  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise RuntimeError("redis package is required for RedisCache") from exc
        self.client = redis.StrictRedis.from_url(url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        """Get JSON-decoded value from Redis."""
        data = self.client.get(key)  # type: ignore[attr-defined]
        if data is None:
            return None
        return json.loads(cast(str, data))

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store JSON-encoded value in Redis with expiry."""
        self.client.setex(key, ttl, json.dumps(value))  # type: ignore[attr-defined]

    def delete(self, key: str) -> None:
        """Remove value from Redis."""
        self.client.delete(key)  # type: ignore[attr-defined]


def get_cache() -> CacheBackend:
    """Return the appropriate cache backend.

    Returns
    -------
    CacheBackend
        RedisCache if REDIS_URL is set, otherwise InMemoryCache.
    """
    if settings.REDIS_URL:
        return RedisCache(settings.REDIS_URL)
    return InMemoryCache()


# Global cache instance
cache: CacheBackend = get_cache()
