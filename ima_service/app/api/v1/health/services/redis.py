# FILE: ima_service/app/api/v1/health/services/redis.py
"""
Redis connectivity health service.
"""

from __future__ import annotations

from ima_service.app.core.redis_cache import get_redis_client

from ..schemas import HealthCheckResponse
from .base import LOG, RESET, YELLOW, run_check


async def _check_redis() -> bool:
    """Return True if a Redis PING succeeds."""
    try:
        pong = await get_redis_client().ping()
        return bool(pong)
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%sRedis%s PING failed: %s", YELLOW, RESET, exc)
        return False


async def redis_health_service() -> HealthCheckResponse:
    """Public service wrapper for Redis health."""
    return await run_check("Redis", _check_redis, timeout=1.5, key="redis")
