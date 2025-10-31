"""Defines the standardized API response model used across the application."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Represents a standardized API response with metadata and user context."""

    trace_id: str
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[UUID] = None
    tenant_id: Optional[str] = None
    roles: Optional[list[str]] = Field(default_factory=list)
    permissions: Optional[list[str]] = Field(default_factory=list)
    data: Optional[Any] = None
    error: Optional[str] = None
    meta: Optional[list[str]] = Field(default_factory=list)
