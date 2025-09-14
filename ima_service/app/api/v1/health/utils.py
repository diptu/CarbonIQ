# ruff: noqa: D401
"""
FILE: app/api/v1/health/utils.py
Utilities for standardized health checks.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Protocol

from fastapi import status

from .schemas import HealthCheckResponse, HealthPayload


class HealthCheckFn(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for async health check callables."""

    async def __call__(self) -> bool:  # noqa: D401
        ...


class HealthCheckError(RuntimeError):  # pylint: disable=too-few-public-methods
    """Raised when a health check fails in an unexpected way."""


@dataclass(slots=True, frozen=True)
class HealthService:  # pylint: disable=too-few-public-methods
    """Encapsulates a single health check."""

    name: str
    check_fn: HealthCheckFn
    details_key: Optional[str] = None
    timeout_sec: float = 3.0

    def __repr__(self) -> str:  # pragma: no cover
        cls = self.__class__.__name__
        return f"{cls}(name={self.name!r}, timeout_sec={self.timeout_sec})"

    async def __call__(self) -> HealthCheckResponse:
        """Execute the check and return a typed response."""
        try:
            async with asyncio.timeout(self.timeout_sec):
                healthy = await self.check_fn()
        except TimeoutError as exc:  # pragma: no cover
            return self._error_response("timeout", str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            return self._error_response("exception", str(exc))

        status_val = "ok" if healthy else "fail"
        details = (
            {self.details_key: status_val}
            if self.details_key is not None
            else None
        )
        payload = HealthPayload(status=status_val, details=details)

        code = (
            status.HTTP_200_OK
            if healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        env = "success" if healthy else "error"
        msg = (
            f"{self.name} health check passed"
            if healthy
            else f"{self.name} health check failed"
        )

        return HealthCheckResponse(
            code=code,
            status=env,
            message=msg,
            data=payload,
            details=None,
        )

    def _error_response(self, kind: str, err: str) -> HealthCheckResponse:
        details = (
            {self.details_key: "fail"} if self.details_key is not None else None
        )
        return HealthCheckResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status="error",
            message=f"{self.name} health check failed",
            data=None,
            details={"error": err, "kind": kind, "details": details},
        )
