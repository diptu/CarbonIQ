# ruff: noqa: D401
"""
FILE: app/api/v1/health/utils.py
Utilities for standardized health checks.
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from fastapi import status

from .schemas import HealthCheckResponse, HealthPayload

CheckFn = Callable[[], Awaitable[bool]]


class HealthService:
    """Run a health check and return a standard response.

    Parameters
    ----------
    name : str
        Display name for the check.
    check_fn : Callable[[], Awaitable[bool]]
        Async function that returns True on success.
    details_key : str | None
        Optional key to place inside `data.details`.
    timeout_sec : float
        Max seconds to wait for the check to complete.

    Examples
    --------
    >>> async def ok(): return True
    >>> svc = HealthService("Server", ok, "server")
    >>> # await svc()
    """

    def __init__(
        self,
        name: str,
        check_fn: CheckFn,
        details_key: str | None = None,
        timeout_sec: float = 3.0,
    ) -> None:
        self.name = name
        self.check_fn = check_fn
        self.details_key = details_key
        self.timeout_sec = timeout_sec

    async def __call__(self) -> HealthCheckResponse:
        """Execute the check and build a response."""
        try:
            ok = await asyncio.wait_for(self.check_fn(), timeout=self.timeout_sec)
        except asyncio.TimeoutError:
            return self._error("timeout", "operation timed out")
        except Exception as exc:  # pylint: disable=broad-except
            return self._error("exception", str(exc))

        status_text = "ok" if ok else "fail"
        details = {self.details_key: status_text} if self.details_key else None
        payload = HealthPayload(status=status_text, details=details)
        code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
        env = "success" if ok else "error"
        msg = (
            f"{self.name} health check passed"
            if ok
            else f"{self.name} health check failed"
        )
        return HealthCheckResponse(
            code=code, status=env, message=msg, data=payload, details=None
        )

    def _error(self, kind: str, err: str) -> HealthCheckResponse:
        details = {self.details_key: "fail"} if self.details_key else None
        return HealthCheckResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status="error",
            message=f"{self.name} health check failed",
            data=None,
            details={"error": err, "kind": kind, "details": details},
        )
