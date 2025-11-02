"""Defines standardized API response schema and helper functions."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel, Field


def build_response_from_request(request: Request, **kwargs):
    return build_response(
        trace_id=request.headers.get("X-Trace-ID", str(uuid.uuid4())),
        correlation_id=request.headers.get("X-Correlation-ID", str(uuid.uuid4())),
        **kwargs,
    )


class APIResponse(BaseModel):
    """
    Standardized API response model including tracing, user context,
    RBAC metadata, and structured results.
    """

    trace_id: str
    correlation_id: str
    timestamp: datetime
    success: bool

    user_id: Optional[UUID] = None
    tenant_id: Optional[str] = None

    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)

    data: Optional[Any] = None
    error: Optional[str] = None

    meta: Dict[str, Any] = Field(default_factory=dict)


def build_response(**kwargs: Any) -> APIResponse:
    """
    Build a standardized APIResponse.
    Auto-generates trace_id, correlation_id, and timestamp if not provided.

    Accepted kwargs:
      - data: Any
      - error: Optional[str]
      - user_id: Optional[UUID]
      - tenant_id: Optional[str]
      - roles: Optional[List[str]]
      - permissions: Optional[List[str]]
      - meta: Optional[dict]
      - trace_id: Optional[str]
      - correlation_id: Optional[str]
    """

    error = kwargs.get("error")
    success = error is None

    return APIResponse(
        trace_id=kwargs.get("trace_id", str(uuid.uuid4())),
        correlation_id=kwargs.get("correlation_id", str(uuid.uuid4())),
        timestamp=datetime.utcnow(),
        success=success,
        user_id=kwargs.get("user_id"),
        tenant_id=kwargs.get("tenant_id"),
        roles=kwargs.get("roles", []),
        permissions=kwargs.get("permissions", []),
        data=kwargs.get("data"),
        error=error,
        meta=kwargs.get("meta", {}),
    )
