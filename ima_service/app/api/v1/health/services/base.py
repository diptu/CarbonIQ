# ruff: noqa: D401
"""Base helpers for health services (shared runner)."""

from __future__ import annotations

from typing import Awaitable, Callable

from ..schemas import HealthCheckResponse
from ..utils import HealthService

CheckFn = Callable[[], Awaitable[bool]]


async def run_check(
    name: str,
    check_fn: CheckFn,
    *,
    details_key: str | None = None,
    timeout: float = 2.5,
) -> HealthCheckResponse:
    """Execute a check with standardized response formatting."""
    svc = HealthService(
        name=name,
        check_fn=check_fn,
        details_key=details_key,
        timeout_sec=timeout,
    )
    return await svc()
