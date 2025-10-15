import redis.asyncio as redis
from typing import Optional, Any


class RedisAdapter:
    """
    Async Redis adapter for caching, token storage, and blacklisting.
    Compatible with redis-py 5.x (asyncio version).
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._pool: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        if not self._pool:
            self._pool = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def close(self) -> None:
        """Close Redis connection."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    # ------------------------- BASIC OPERATIONS -------------------------

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key with optional TTL."""
        if not self._pool:
            await self.connect()
        return await self._pool.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        """Get a key value."""
        if not self._pool:
            await self.connect()
        return await self._pool.get(key)

    async def delete(self, key: str) -> int:
        """Delete a key."""
        if not self._pool:
            await self.connect()
        return await self._pool.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._pool:
            await self.connect()
        return bool(await self._pool.exists(key))

    # -------------------------- TOKEN HELPERS --------------------------

    async def blacklist_token(self, jti: str, ttl: int) -> None:
        """Blacklist a JWT for the given TTL."""
        await self.set(f"blacklist:{jti}", "1", expire=ttl)

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if JWT is blacklisted."""
        return await self.exists(f"blacklist:{jti}")
