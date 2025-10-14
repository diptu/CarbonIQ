"""Audit log schemas for tracking sensitive actions."""

from __future__ import annotations

from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import ORMBaseSchema


# ===============================
# Audit Log Schemas
# ===============================


class AuditLogBase(BaseModel):
    """Base schema for audit logs.

    Notes
    -----
    - Shared fields for audit log entries.
    - Tracks user actions, resources, and status codes.
    """

    user_id: Optional[UUID] = Field(None, description="ID of the user performing the action")
    tenant_id: Optional[UUID] = Field(
        None, description="ID of the tenant associated with the action"
    )
    tenant_path: Optional[str] = Field(
        None, description="Hierarchical tenant path (e.g., org/tenant/subtenant)"
    )
    action: str = Field(..., max_length=100, description="Action performed")
    resource: str = Field(..., max_length=100, description="Resource affected")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method used")
    endpoint: Optional[str] = Field(None, max_length=255, description="API endpoint accessed")
    # 🔑 FIX: Use Pydantic V2 direct annotation syntax for constraints
    status_code: int = Field(..., ge=100, le=599, description="HTTP-like status code")
    ip_address: Optional[str] = Field(None, max_length=45, description="Origin IP address")
    device_info: Optional[str] = Field(None, max_length=255, description="Device or client info")
    correlation_id: Optional[str] = Field(
        None, max_length=100, description="Correlation ID for tracing"
    )
    trace_id: Optional[str] = Field(
        None, max_length=100, description="Trace ID for distributed tracing"
    )
    extra: Optional[Dict] = Field(None, description="Flexible JSON metadata")

    # ===============================
    # Validators (Updated to Pydantic V2 classmethod syntax)
    # ===============================

    @field_validator("tenant_path")
    @classmethod
    def validate_tenant_path(cls, value: Optional[str]) -> Optional[str]:
        """Ensure tenant_path follows hierarchical pattern if provided."""
        if value and not all(part.strip() for part in value.split("/")):
            raise ValueError(
                "tenant_path must be a non-empty hierarchical string, e.g., 'org/tenant/subtenant'"
            )
        return value

    @field_validator("action", "resource", mode="before")
    @classmethod
    def validate_non_empty_str(cls, value: str) -> str:
        """Ensure critical fields are non-empty."""
        if not value or not str(value).strip():
            raise ValueError("Field cannot be empty or whitespace")
        return str(value).strip()

    @model_validator(mode="before")
    @classmethod
    def check_extra_is_dict(cls, values: dict) -> dict:
        """Ensure `extra` is a dictionary if provided."""
        # Using .get() for safety and explicit check before assignment
        extra = values.get("extra")
        if extra is not None and not isinstance(extra, dict):
            raise ValueError("extra must be a dictionary if provided")
        return values


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry."""


class AuditLogRead(AuditLogBase, ORMBaseSchema):
    """Schema for reading audit log entries. Immutable by definition."""

    id: int = Field(..., description="Unique audit log identifier")

    model_config = {
        "from_attributes": True,
        "extra": "ignore",
        "frozen": True,
    }


class AuditLogInDB(AuditLogRead):
    """Internal schema for DB-level audit logs."""


__all__ = [
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogRead",
    "AuditLogInDB",
]
