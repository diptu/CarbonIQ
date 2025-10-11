"""Audit log schemas for tracking sensitive actions."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from .base import ORMBaseSchema


class AuditLogBase(BaseModel):
    """Base schema for audit logs.

    Notes
    -----
    - Shared fields for audit log entries.
    - Tracks user actions, resources, and status codes.
    """

    user_id: Optional[uuid.UUID] = Field(
        None, description="ID of the user performing the action"
    )
    tenant_id: Optional[uuid.UUID] = Field(
        None, description="ID of the tenant associated with action"
    )
    action: str = Field(..., max_length=100, description="Action performed")
    resource: str = Field(..., max_length=100, description="Resource affected")
    status_code: int = Field(..., description="HTTP-like status code")


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry.

    Notes
    -----
    - `timestamp` is automatically added by DB; no input needed.
    """


class AuditLogRead(AuditLogBase, ORMBaseSchema):
    """Schema for reading audit log entries."""

    id: int = Field(..., description="Unique audit log identifier")


class AuditLogInDB(AuditLogRead):
    """Internal schema for DB-level audit logs.

    Notes
    -----
    - Can include extra internal fields if needed for reporting.
    """


__all__ = [
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogRead",
    "AuditLogInDB",
]
