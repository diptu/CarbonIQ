# app/core/upstash_redis_adapter.py
from __future__ import annotations
from typing import Optional, Any
from upstash_redis import Redis
from .config import get_settings
from .logger import logger

settings = get_settings()


class RedisAdapter:
    """
    Async Redis adapter using Upstash.
    Supports caching, token storage, and blacklisting.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None) -> None:
        self._url = url or settings.REDIS_URL
        self._token = token or settings.REDIS_TOKEN
        self._client: Optional[Redis] = None

    def connect(self) -> Redis:
        """Initialize the Upstash client (idempotent)."""
        if not self._client:
            self._client = Redis(url=self._url, token=self._token)
            logger.info("Upstash Redis client initialized")
        return self._client

    # ------------------------- BASIC OPERATIONS -------------------------

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key with optional TTL (seconds)."""
        client = self.connect()
        try:
            if expire:
                result = await client.set(key, value, ex=expire)
            else:
                result = await client.set(key, value)
            return result is True
        except Exception as e:
            logger.error(f"Upstash Redis SET failed for key={key}: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get a key value."""
        client = self.connect()
        try:
            return await client.get(key)
        except Exception as e:
            logger.error(f"Upstash Redis GET failed for key={key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key."""
        client = self.connect()
        try:
            deleted = await client.delete(key)
            return bool(deleted)
        except Exception as e:
            logger.error(f"Upstash Redis DELETE failed for key={key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        client = self.connect()
        try:
            exists = await client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Upstash Redis EXISTS check failed for key={key}: {e}")
            return False

    # -------------------------- TOKEN HELPERS --------------------------

    async def blacklist_token(self, jti: str, ttl: int) -> None:
        """Blacklist a JWT for a given TTL in seconds."""
        await self.set(f"blacklist:{jti}", "1", expire=ttl)

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if a JWT is blacklisted."""
        return await self.exists(f"blacklist:{jti}")


# ------------------------------
# Singleton instance
# ------------------------------
redis = RedisAdapter()
