# ruff: noqa: D401
"""Server liveness health service."""

from __future__ import annotations

import asyncio

from ..schemas import HealthCheckResponse
from .base import run_check


async def server_health_service() -> HealthCheckResponse:
    """Return server liveness status."""
    async def _check() -> bool:
        await asyncio.sleep(0)
        return True

    return await run_check(
        "Server", _check, details_key="server", timeout=2.0
    )
