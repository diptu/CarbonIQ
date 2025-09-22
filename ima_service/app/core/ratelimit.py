"""Tiny Redis-backed rate limiter (fixed window) for login & other endpoints."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Request, status
from redis.asyncio import Redis

from .errors import AppError
from .settings import Settings, get_settings


def _redis_url(st: Settings) -> str:
    if st.redis_dsn:
        try:
            return st.redis_dsn.get_secret_value()
        except Exception:
            return str(st.redis_dsn)
    if st.redis_url:
        try:
            return st.redis_url.get_secret_value()
        except Exception:
            return str(st.redis_url)
    if st.redis:
        scheme = "rediss" if st.redis.ssl else "redis"
        auth = f":{st.redis.password.get_secret_value()}@" if st.redis.password else ""
        return f"{scheme}://{auth}{st.redis.host}:{st.redis.port}/{st.redis.db}"
    return "redis://localhost:6379/0"


@dataclass(slots=True, frozen=True)
class LimitState:
    allowed: bool
    remaining: int
    reset_epoch: int


class RateLimiter:
    """Fixed-window limiter using INCR + EXPIRE (O(1), good enough for auth)."""

    def __init__(
        self,
        redis: Redis,
        *,
        prefix: str = "ima:rl",
        limit: int = 10,
        window_s: int = 60,
    ) -> None:
        self._r = redis
        self._p = prefix
        self._limit = int(limit)
        self._window = int(window_s)

    def _key(self, bucket: str) -> str:
        return f"{self._p}:{bucket}"

    async def allow(self, bucket: str) -> LimitState:
        """Consume 1 token in 'bucket'; return state (allowed/remaining/reset)."""
        k = self._key(bucket)
        cur = int(await self._r.incr(k))
        if cur == 1:
            await self._r.expire(k, self._window)
            reset = int(datetime.now(timezone.utc).timestamp()) + self._window
        else:
            ttl = int(await self._r.ttl(k))
            reset = int(datetime.now(timezone.utc).timestamp()) + (
                ttl if ttl > 0 else self._window
            )
        remaining = max(self._limit - cur, 0)
        return LimitState(
            allowed=cur <= self._limit, remaining=remaining, reset_epoch=reset
        )


# -------------------------- helpers for login flow --------------------------- #


async def get_limiter(st: Settings | None = None) -> RateLimiter:
    s = st or get_settings()
    r = Redis.from_url(_redis_url(s), decode_responses=True)
    # env overrides (keep settings minimal):
    limit = int(os.getenv("IMA_AUTH__RL__LIMIT", "10"))
    window = int(os.getenv("IMA_AUTH__RL__WINDOW", "60"))
    return RateLimiter(r, prefix="ima:rl", limit=limit, window_s=window)


def _client_ip(req: Request) -> str:
    # Best-effort small extractor; for production put a trusted proxy in front.
    xfwd = req.headers.get("x-forwarded-for")
    if xfwd:
        return xfwd.split(",")[0].strip()
    return req.client.host if req.client else "unknown"


async def enforce_login_limits(
    *,
    request: Request,
    username: str,
    limiter: Optional[RateLimiter] = None,
) -> None:
    """Apply per-username and per-IP limits; raise AppError on exceed."""
    lim = limiter or await get_limiter()
    ip = _client_ip(request)
    user_bucket = f"login:user:{username.lower()}"
    ip_bucket = f"login:ip:{ip}"
    u = await lim.allow(user_bucket)
    i = await lim.allow(ip_bucket)
    if not (u.allowed and i.allowed):
        raise AppError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMITED",
            message="Too many login attempts. Try again later.",
            details={
                "user_remaining": u.remaining,
                "user_reset": u.reset_epoch,
                "ip_remaining": i.remaining,
                "ip_reset": i.reset_epoch,
            },
        )


__all__ = ["RateLimiter", "LimitState", "get_limiter", "enforce_login_limits"]
