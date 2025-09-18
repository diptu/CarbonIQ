# FILE: ima_service/app/api/v1/health/router.py
"""
API v1 health routes (thin handlers delegating to services).
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .docs import (
    DATABASE_HEALTH_DOCS,
    FULL_HEALTH_DOCS,
    REDIS_HEALTH_DOCS,
    SERVER_HEALTH_DOCS,
)
from .schemas import HealthCheckResponse
from .services import (
    database_health_service,
    full_health_service,
    redis_health_service,
    server_health_service,
)

# FastAPI convention is a module-level `router` object (not a constant).
router = APIRouter(prefix="/health", tags=["health"])


def _json(payload: HealthCheckResponse) -> JSONResponse:
    """Serialize a HealthCheckResponse to a JSONResponse
    with its status code."""
    return JSONResponse(status_code=payload.code, content=payload.model_dump())


@router.get("/server", **SERVER_HEALTH_DOCS)
async def server_health() -> JSONResponse:
    """Liveness: verify the API process/event loop is responsive."""
    return _json(await server_health_service())


@router.get("/database", **DATABASE_HEALTH_DOCS)
async def database_health() -> JSONResponse:
    """Readiness: verify PostgreSQL `SELECT 1` works."""
    return _json(await database_health_service())


@router.get("/redis", **REDIS_HEALTH_DOCS)
async def redis_health() -> JSONResponse:
    """Readiness: verify Redis `PING` works."""
    return _json(await redis_health_service())


@router.get("/", **FULL_HEALTH_DOCS)
async def full_health() -> JSONResponse:
    """Aggregate health: server + database + redis."""
    return _json(await full_health_service())
