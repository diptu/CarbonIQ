# FILE: ima_service/app/api/v1/health/services/server.py
"""
Server liveness health service.
"""

from __future__ import annotations

import asyncio

from ..schemas import HealthCheckResponse
from .base import run_check


async def _check_server() -> bool:
    """True if the event loop is alive (async no-op)."""
    await asyncio.sleep(0)
    return True


async def server_health_service() -> HealthCheckResponse:
    """Liveness check for the API server."""
    return await run_check("Server", _check_server, timeout=1.0)
