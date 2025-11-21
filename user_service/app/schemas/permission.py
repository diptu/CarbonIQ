"""Pydantic schemas for permission creation, update, and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# -----------------------------
# Base schema
# -----------------------------
class PermissionBase(BaseModel):
    """Pydantic Base schemas for permission  models."""

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

    @field_validator("name", mode="before")
    def normalize_name(cls, v: str) -> str:  # pylint: disable=no-self-argument
        """Normalize name ."""
        return v.strip().lower() if v else v


# -----------------------------
# Create schema
# -----------------------------
class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""


# -----------------------------
# Update schema
# -----------------------------
class PermissionUpdate(BaseModel):
    """Schema for updating permissions; all fields optional."""

    name: Optional[str] = None
    description: Optional[str] = None


# -----------------------------
# Response schema
# -----------------------------
class PermissionOut(PermissionBase):
    """Schema for returning permission details in responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
