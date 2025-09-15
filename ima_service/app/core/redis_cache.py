"""
FILE: ima_service/app/core/redis_cache.py
Async Redis client factory (lazy, import-safe).
"""

from __future__ import annotations

from functools import lru_cache

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover
    redis = None  # type: ignore[assignment]

from ima_service.app.core.config import get_settings


class RedisClientError(RuntimeError):
    """Raised when the Redis client cannot be created."""


@lru_cache(maxsize=1)
def get_redis_client() -> "redis.Redis":
    """Return a cached asyncio Redis client.

    Notes
    -----
    - Does NOT access settings at import time.
    - Raises RedisClientError if redis is not installed.
    """
    if redis is None:  # pragma: no cover
        raise RedisClientError(
            "redis.asyncio is not installed. Add 'redis>=5'."
        )

    settings = get_settings()  # may raise if env is invalid (expected)
    return redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        password=settings.redis.password,
        db=settings.redis.db,
        decode_responses=True,
    )
