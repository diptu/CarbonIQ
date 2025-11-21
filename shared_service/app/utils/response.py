"""
Standardized API response schemas for all services.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import Request
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """Represents the authenticated user's context."""

    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


class MetaInfo(BaseModel):
    """Metadata about the API response, useful for debugging and analytics."""

    request_duration_ms: Optional[float] = None
    source: str = Field(default="user_service")
    cache_hit: Optional[bool] = False
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standardized API response schema."""

    trace_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    status_code: int = 200
    path: Optional[str] = None
    method: Optional[str] = None
    message: Optional[str] = None

    api_version: str = "v1"

    # ✅ can be optionally excluded from response
    user_context: Optional[UserContext] = Field(default=None)

    result: Optional[Any] = None
    meta: MetaInfo = Field(default_factory=MetaInfo)
    error: Optional[Dict[str, Any]] = None


def build_api_response(
    request: Request,
    current_user: Optional[Any] = None,
    result: Any = None,
    status_code: int = 200,
    success: bool = True,
    message: Optional[str] = None,
    error: Optional[Dict[str, Any]] = None,
    meta_extra: Optional[Dict[str, Any]] = None,
    include_user_context: bool = True,  # ✅ NEW FLAG
) -> APIResponse:
    """
    Builds a standardized APIResponse object.
    Optionally excludes user_context to avoid exposing sensitive data.
    Includes request duration from middleware if available.
    """

    # ✅ safe default for trace and correlation IDs
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    user_context = None

    # ✅ only attach user context if allowed
    if include_user_context and current_user:
        try:
            user_context = UserContext(
                user_id=str(current_user.id),
                tenant_id=getattr(current_user, "tenant_id", None),
                roles=getattr(current_user, "roles_cached", []),
                permissions=getattr(current_user, "permissions_cached", []),
            )
        except Exception:
            # ✅ if anything fails, ignore (never break API response)
            user_context = None

    # ✅ get request duration from request.state if available
    request_duration_ms = getattr(request.state, "request_duration_ms", None)

    meta = MetaInfo(
        request_duration_ms=request_duration_ms,
        extra=meta_extra or {},
    )

    return APIResponse(
        trace_id=trace_id,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc),
        path=str(request.url.path),
        method=request.method,
        status_code=status_code,
        success=success,
        user_context=user_context,
        result=result,
        meta=meta,
        error=error,
        message=message,
    )
