# ruff: noqa: D401
"""
FILE: app/api/v1/health/router.py
Route declarations for API v1 health endpoints (no business logic here).
"""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.db.session import get_db

from .docs import (
    DATABASE_HEALTH_DOCS,
    FULL_HEALTH_DOCS,
    HEALTH_DOCS,
    REDIS_HEALTH_DOCS,
)
from .schemas import HealthCheckResponse
from .services import (
    database_health_service,
    full_health_service,
    redis_health_service,
    server_health_service,
)

router: Final = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/server",
    response_model=HealthCheckResponse,
    **dict(HEALTH_DOCS.server),
)
async def server_health() -> HealthCheckResponse:
    """Liveness check for the API server."""
    return await server_health_service()


@router.get(
    "/database",
    response_model=HealthCheckResponse,
    **dict(DATABASE_HEALTH_DOCS),
)
async def database_health() -> HealthCheckResponse:
    """Connectivity check for the PostgreSQL database."""
    return await database_health_service()


@router.get(
    "/redis",
    response_model=HealthCheckResponse,
    **dict(REDIS_HEALTH_DOCS),
)
async def redis_health() -> HealthCheckResponse:
    """Connectivity check for Redis (returns 500 on failure)."""
    return await redis_health_service()


@router.get(
    "/",
    response_model=HealthCheckResponse,
    **dict(FULL_HEALTH_DOCS),
)
async def full_health(db: AsyncSession = Depends(get_db)) -> HealthCheckResponse:
    """Combined health: server, database, redis."""
    return await full_health_service(db)
