"""Pydantic schemas for Role creation, update, and response models with improved structure."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# Base schema
# -----------------------------
class RoleBase(BaseModel):
    """Common attributes shared across all role schemas."""

    name: str = Field(
        ...,
        max_length=50,
        description="Role name",
        json_schema_extra={"example": "admin"},
    )
    description: Optional[str] = Field(
        None,
        description="Role description",
        json_schema_extra={"example": "Administrator role with full access"},
    )


# -----------------------------
# Create schema
# -----------------------------
class RoleCreate(RoleBase):
    """Schema for creating a new role."""


# -----------------------------
# Update schema
# -----------------------------
class RoleUpdate(BaseModel):
    """Schema for updating an existing role."""

    name: Optional[str] = Field(
        None,
        description="New role name",
        json_schema_extra={"example": "editor"},
    )
    description: Optional[str] = Field(
        None,
        description="Updated description",
        json_schema_extra={"example": "Can edit content but not manage users"},
    )


# -----------------------------
# Response schema
# -----------------------------
class RoleOut(RoleBase):
    """Schema for returning role details in responses."""

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM parsing
