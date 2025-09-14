# ruff: noqa: D401
"""
FILE: app/api/v1/health/router.py
Health endpoints for the API v1.
"""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter

from .docs import HEALTH_DOCS
from .schemas import HealthCheckResponse
from .utils import HealthService

ROUTER: Final = APIRouter(prefix="/health", tags=["health"])


async def _server_check() -> bool:
    """Simple liveness check for the API server."""
    return True


SERVER_SERVICE: Final = HealthService(
    name="Server",
    check_fn=_server_check,
    details_key="server",
    timeout_sec=2.0,
)


@ROUTER.get(
    "/server",
    response_model=HealthCheckResponse,
    **dict(HEALTH_DOCS.server),
)
async def server_health() -> HealthCheckResponse:
    """Liveness check for the API server."""
    return await SERVER_SERVICE()


# Back-compat alias if other modules still import `router`
router = ROUTER  # pylint: disable=invalid-name
