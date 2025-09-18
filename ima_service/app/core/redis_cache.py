# FILE: ima_service/app/core/redis_cache.py
"""
Async Redis client factory (lazy, import-safe).

- No settings read at import time.
- Supports REDIS_URL or discrete settings.
- Returns a single cached client instance.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from ima_service.app.core.config import RedisSettings, get_settings

# Import redis.asyncio safely and normalize to a typed variable that may be None
try:
    import redis.asyncio as _redis_async_mod  # redis>=5
except ImportError:  # pragma: no cover
    _redis_async_mod = None  # type: ignore[assignment]

# Make the module reference explicitly Optional for type checkers
REDIS_ASYNC: Any | None = _redis_async_mod

__all__ = ["get_redis_client", "close_redis_client", "RedisClientError"]

if TYPE_CHECKING:
    from redis.asyncio import Redis as _RedisClient  # pragma: no cover
else:
    _RedisClient = Any  # type: ignore[misc]


class RedisClientError(RuntimeError):
    """Raised when the Redis client cannot be created."""


def _get_redis_settings() -> RedisSettings:
    """
    Return typed Redis settings.

    Pylint can misread Pydantic model attributes as FieldInfo when accessed
    indirectly; centralizing access keeps both pylint and mypy happy.
    """
    settings = get_settings()
    return settings.redis


@lru_cache(maxsize=1)
def get_redis_client() -> _RedisClient:
    """
    Return a cached asyncio Redis client.

    Raises
    ------
    RedisClientError
        If redis>=5 is missing or client creation fails.
    """
    if REDIS_ASYNC is None:  # pragma: no cover
        raise RedisClientError("redis>=5 is required (missing redis.asyncio).")

    s = _get_redis_settings()

    # Use getattr() to avoid pylint false positives on Pydantic models
    url = getattr(s, "url", None)
    effective_url = getattr(s, "effective_url", None)
    host = getattr(s, "host", "127.0.0.1")
    port = getattr(s, "port", 6379)
    password = getattr(s, "password", "")
    db = getattr(s, "db", 0)

    try:
        if url:
            tmp_any: Any = REDIS_ASYNC.from_url(
                effective_url, decode_responses=True
            )
            return tmp_any  # type: ignore[no-any-return]

        tmp_any = REDIS_ASYNC.Redis(
            host=host,
            port=port,
            password=password or None,
            db=db,
            decode_responses=True,
        )
        return tmp_any  # type: ignore[no-any-return]
    except (OSError, ValueError, RuntimeError) as exc:  # pragma: no cover
        # Narrowed exceptions to avoid broad-exception-caught while still
        # covering typical client construction failures.
        raise RedisClientError(f"Redis client creation failed: {exc}") from exc


async def close_redis_client() -> None:
    """Close the cached client (useful for tests and shutdown hooks)."""
    try:
        client = get_redis_client()
    except RedisClientError:  # pragma: no cover
        return

    close_fn = getattr(client, "close", None)
    if callable(close_fn):
        await close_fn()
