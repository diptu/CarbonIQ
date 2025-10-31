"""Schemas for UserRole operations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# Base
# -----------------------------
class UserRoleBase(BaseModel):
    """Shared fields between schemas."""

    user_id: UUID = Field(..., description="Associated User ID")
    role_id: UUID = Field(..., description="Associated Role ID")


# -----------------------------
# Create
# -----------------------------
class UserRoleCreate(UserRoleBase):
    """Schema for assigning a role to a user."""


# -----------------------------
# Response
# -----------------------------
class UserRoleOut(UserRoleBase):
    """Schema for returning user-role assignments."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)  # enable ORM parsing
