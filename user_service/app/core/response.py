"""Defines standardized API response schema and helper functions."""

import uuid
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standardized API response model including metadata and user context."""

    trace_id: str
    correlation_id: str
    timestamp: datetime
    user_id: Optional[UUID] = None
    tenant_id: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    data: Any = None
    error: Optional[str] = None
    meta: List[str] = []


def build_response(**kwargs: Any) -> APIResponse:
    """
    Build a standardized APIResponse from keyword arguments.

    Expected kwargs:
        - data: Any
        - error: Optional[str]
        - user_id: Optional[UUID]
        - tenant_id: Optional[str]
        - roles: Optional[List[str]]
        - permissions: Optional[List[str]]
        - meta: Optional[List[str]]
        - trace_id: Optional[str]
        - correlation_id: Optional[str]

    Auto-generates trace_id, correlation_id, and timestamp if not provided.
    """
    return APIResponse(
        trace_id=kwargs.get("trace_id", str(uuid.uuid4())),
        correlation_id=kwargs.get("correlation_id", str(uuid.uuid4())),
        timestamp=datetime.utcnow(),
        user_id=kwargs.get("user_id"),
        tenant_id=kwargs.get("tenant_id"),
        roles=kwargs.get("roles", []),
        permissions=kwargs.get("permissions", []),
        data=kwargs.get("data"),
        error=kwargs.get("error"),
        meta=kwargs.get("meta", []),
    )
