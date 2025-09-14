# ruff: noqa: D401
"""
FILE: app/api/v1/health/schemas.py
Schemas for Health API endpoints.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


def _utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp with 'Z' suffix."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class HealthPayload(BaseModel):
    """Data payload for a health response."""

    status: str = Field(..., description="Service status: 'ok' or 'fail'.")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional service details."
    )


class HealthCheckResponse(BaseModel):
    """Standardized response schema for health endpoints.

    Notes
    -----
    This model is frozen and forbids extra fields to ensure consistent API
    contracts in production.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: int = Field(..., description="HTTP status code.")
    status: str = Field(..., description="Envelope status: success/error.")
    message: str = Field(..., description="Human-readable message.")
    timestamp: str = Field(
        default_factory=_utc_now_iso, description="UTC timestamp (ISO-8601)."
    )
    data: Optional[HealthPayload] = Field(
        default=None, description="Primary data payload."
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Envelope-level error details."
    )
