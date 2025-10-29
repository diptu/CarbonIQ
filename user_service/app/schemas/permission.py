"""Pydantic schemas for permission creation, update, and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# -----------------------------
# Base schema
# -----------------------------
class PermissionBase(BaseModel):
    """Base schema for permissions."""

    name: str = Field(
        ...,
        max_length=100,
        description="The internal name of the permission",
        json_schema_extra={"example": "view_users"},
    )
    description: Optional[str] = Field(
        None,
        description="A short description of what this permission allows",
        json_schema_extra={"example": "Allows viewing user list"},
    )


# -----------------------------
# Create schema
# -----------------------------
class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""


# -----------------------------
# Update schema
# -----------------------------
class PermissionUpdate(BaseModel):
    """Schema used for updating permissions."""

    name: Optional[str] = Field(
        default=None,
        description="The internal name of the permission",
        json_schema_extra={"example": "edit_users"},
    )
    description: Optional[str] = Field(
        default=None,
        description="A short description of what this permission allows",
        json_schema_extra={"example": "Allows editing user data"},
    )


# -----------------------------
# Response schema
# -----------------------------
class PermissionOut(PermissionBase):
    """Schema for returning permission details in responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
