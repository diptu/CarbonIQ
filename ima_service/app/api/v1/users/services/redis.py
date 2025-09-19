# FILE: ima_service/app/api/v1/users/services/redis.py
"""Async Redis helpers for ephemeral tokens (email verify / reset)."""

from __future__ import annotations

import logging
from typing import Any, Optional, cast

from redis import asyncio as aioredis
from redis.exceptions import RedisError

from ima_service.app.core.log_colors import CLR_ERR, CLR_OK, CLR_RESET, CLR_WARN

_LOG = logging.getLogger(__name__)


class AsyncRedisTokenStore:
    """Tiny async wrapper for token storage with TTL."""

    def __init__(self, client: aioredis.Redis[Any], prefix: str = "users:") -> None:
        """Create a token store.

        Args:
            client: redis.asyncio client instance.
            prefix: key prefix namespace, e.g., 'users:'.
        """
        self._r = client
        self._p = prefix

    async def set_token(self, key: str, value: str, ttl_seconds: int) -> None:
        """Set a token with TTL."""
        try:
            await self._r.setex(f"{self._p}{key}", ttl_seconds, value.encode("utf-8"))
            _LOG.info(
                "%s[redis:set]%s k=%s ttl=%ss", CLR_OK, CLR_RESET, key, ttl_seconds
            )
        except RedisError as exc:
            _LOG.error(
                "%s[redis:set.error]%s k=%s err=%s", CLR_ERR, CLR_RESET, key, exc
            )
            raise

    async def get_token(self, key: str) -> Optional[str]:
        """Get a token; returns None if missing/expired."""
        try:
            raw = await self._r.get(f"{self._p}{key}")
            b: Optional[bytes] = cast(Optional[bytes], raw)
            if b is None:
                _LOG.debug("%s[redis:get.miss]%s k=%s", CLR_WARN, CLR_RESET, key)
                return None
            s: str = b.decode("utf-8")
            _LOG.debug("%s[redis:get.hit]%s k=%s", CLR_OK, CLR_RESET, key)
            return s
        except RedisError as exc:
            _LOG.error(
                "%s[redis:get.error]%s k=%s err=%s", CLR_ERR, CLR_RESET, key, exc
            )
            raise

    async def delete_token(self, key: str) -> None:
        """Delete a token (idempotent)."""
        try:
            await self._r.delete(f"{self._p}{key}")
            _LOG.info("%s[redis:del]%s k=%s", CLR_OK, CLR_RESET, key)
        except RedisError as exc:
            _LOG.error(
                "%s[redis:del.error]%s k=%s err=%s", CLR_ERR, CLR_RESET, key, exc
            )
            raise
