"""Pydantic schemas for Role creation, update, and response models."""

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
        ..., max_length=50, json_schema_extra={"example": "admin"}, description="Role name"
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Administrator role with full access"},
        description="Role description",
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
        None, json_schema_extra={"example": "editor"}, description="New role name"
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Can edit content but not manage users"},
        description="Updated description",
    )


# -----------------------------
# Response schema
# -----------------------------
class RoleOut(RoleBase):
    """Schema for returning role details in responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # enable ORM parsing
