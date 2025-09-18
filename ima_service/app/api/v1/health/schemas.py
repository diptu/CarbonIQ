# FILE: ima_service/app/api/v1/health/schemas.py
"""
Pydantic schemas for health endpoints (compact & frozen).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class HealthPayload(BaseModel):
    """Primary health payload."""

    status: str = Field(..., description="'ok' or 'fail'")
    details: dict[str, Any] | None = Field(
        None, description="Per-service details"
    )


class HealthCheckResponse(BaseModel):
    """Standard envelope for health responses."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: int = Field(..., description="HTTP status code")
    status: str = Field(..., description="'success' or 'error'")
    message: str = Field(..., description="Human-readable message")
    timestamp: str = Field(default_factory=_utc_now_iso, description="UTC time")
    data: HealthPayload | None = Field(
        None, description="Payload on success/fail"
    )
    details: dict[str, Any] | None = Field(None, description="Error details")
