# FILE: ima_service/app/api/v1/health/services/full.py
"""
Aggregated health: server + database + redis.
"""

from __future__ import annotations

from sqlalchemy import text

from ima_service.app.core.redis_cache import get_redis_client
from ima_service.app.db.session import get_session_manager

from ..schemas import HealthCheckResponse, HealthPayload


async def full_health_service() -> HealthCheckResponse:
    """Return combined health snapshot (200 if all checks pass; else 503)."""
    results: dict[str, str] = {"server": "ok"}

    # Database
    try:
        manager = get_session_manager()
        async with manager.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        results["database"] = "ok"
    except Exception:  # pylint: disable=broad-except
        results["database"] = "fail"

    # Redis
    try:
        pong = await get_redis_client().ping()
        results["redis"] = "ok" if pong else "fail"
    except Exception:  # pylint: disable=broad-except
        results["redis"] = "fail"

    overall_ok = all(v == "ok" for v in results.values())
    return HealthCheckResponse(
        code=200 if overall_ok else 503,
        status="success" if overall_ok else "error",
        message="Full system health check completed",
        data=HealthPayload(status="ok" if overall_ok else "fail", details=results),
        details=None,
    )
