# ruff: noqa: D401
"""Aggregated health service (server + database + redis)."""

from __future__ import annotations

from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.core.redis_cache import get_redis_client

from ..schemas import HealthCheckResponse, HealthPayload


async def full_health_service(db: AsyncSession) -> HealthCheckResponse:
    """Return combined health.

    Returns
    -------
    HealthCheckResponse
        code: 200 if all ok, else 503.
    """
    results: dict[str, str] = {"server": "ok"}

    # Database
    try:
        await db.execute(text("SELECT 1"))
        results["database"] = "ok"
    except SQLAlchemyError:
        results["database"] = "fail"

    # Redis
    try:
        client = get_redis_client()
        pong = await client.ping()
        results["redis"] = "ok" if pong else "fail"
    except (RedisError, Exception):
        results["redis"] = "fail"

    overall = "ok" if all(v == "ok" for v in results.values()) else "fail"
    code = 200 if overall == "ok" else 503
    env = "success" if overall == "ok" else "error"

    return HealthCheckResponse(
        code=code,
        status=env,
        message="Full system health check completed",
        data=HealthPayload(status=overall, details=results),
        details=None,
    )
