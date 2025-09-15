# ruff: noqa: D401
"""Redis connectivity health service (500 on failure by design)."""

from __future__ import annotations

from ima_service.app.core.redis_cache import get_redis_client

from ..schemas import HealthCheckResponse
from .base import run_check


async def redis_health_service() -> HealthCheckResponse:
    """Return Redis connectivity.

    Notes
    -----
    - On failure, raises to HealthService -> HTTP 500.
    """
    async def _check() -> bool:
        client = get_redis_client()
        pong = await client.ping()
        if not pong:
            raise RuntimeError("Redis ping returned falsy")
        return True

    return await run_check("Redis", _check, details_key="redis")
