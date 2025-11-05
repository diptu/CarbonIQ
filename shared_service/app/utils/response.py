"""Standardized API response schemas for all services."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """Represents the authenticated user's context."""

    user_id: Optional[str] = Field(None, example="e13a6b94-4a3a-4310-a92e-182bb9b3a2e8")
    tenant_id: Optional[str] = Field(
        None, example="9bb3224f-dc98-45ef-a47e-c6bb706e1e55"
    )
    roles: List[str] = Field(default_factory=list, example=["admin", "user"])
    permissions: List[str] = Field(
        default_factory=list, example=["user.read", "user.create"]
    )


class MetaInfo(BaseModel):
    """Metadata about the API response, useful for debugging and analytics."""

    request_duration_ms: Optional[float] = Field(None, example=18.42)
    source: str = Field(default="user_service", example="user_service")
    cache_hit: Optional[bool] = Field(default=False)
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standardized API response schema."""

    trace_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),  # auto-generate if not provided
        example="2bc474c7-3d88-4e48-9111-d8b38a407620",
    )
    correlation_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),  # auto-generate if not provided
        example="b1db9ba6-50c7-4e9d-b1ac-931715a33022",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = Field(True, description="Indicates if the request was successful.")
    status_code: int = Field(200, description="HTTP status code of the response.")
    path: Optional[str] = Field(None, example="/api/v1/users")
    method: Optional[str] = Field(None, example="GET")
    api_version: str = Field(default="v1", example="v1")

    user_context: UserContext = Field(default_factory=UserContext)
    result: Optional[Any] = Field(
        default=None, description="Main payload data for the response."
    )
    meta: MetaInfo = Field(default_factory=MetaInfo)
    error: Optional[Dict[str, Any]] = Field(
        default=None, description="Error details, if any."
    )
