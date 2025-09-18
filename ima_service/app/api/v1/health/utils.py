# FILE: ima_service/app/api/v1/health/utils.py
"""
Generic async health runner with timeout + safe error envelope.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import status

from .schemas import HealthCheckResponse, HealthPayload

CheckFn = Callable[[], Awaitable[bool]]

__all__ = ["HealthService"]


@dataclass(slots=True)
class HealthService:
    """Async health check runner producing a standard response."""

    name: str
    check_fn: CheckFn
    key: str | None = None
    timeout: float = 2.5

    async def __call__(self) -> HealthCheckResponse:
        try:
            ok = await asyncio.wait_for(self.check_fn(), timeout=self.timeout)
        except Exception as exc:  # pylint: disable=broad-except
            status_txt = "fail"
            return HealthCheckResponse(
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                status="error",
                message=f"{self.name} check failed",
                data=HealthPayload(
                    status=status_txt,
                    details={self.key: status_txt} if self.key else None,
                ),
                details={"error": str(exc)},
            )

        status_txt = "ok" if ok else "fail"
        code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            code=code,
            status="success" if ok else "error",
            message=f"{self.name} check {'passed' if ok else 'failed'}",
            data=HealthPayload(
                status=status_txt,
                details={self.key: status_txt} if self.key else None,
            ),
            details=None if ok else {},
        )
