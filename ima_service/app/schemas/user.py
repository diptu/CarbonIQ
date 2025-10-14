"""User schemas for multi-tenant RBAC system."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from .base import ORMBaseSchema  # Use centralized base schema


class UserStatus(str, Enum):
    """Enum representing user account status."""

    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"


class UserBase(BaseModel):
    """Base schema with shared attributes for all users."""

    email: EmailStr = Field(..., max_length=255, description="User email")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    is_active: bool = Field(default=True, description="Indicates if user is active")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User account status")
    tenant_path: Optional[str] = Field(None, max_length=255, description="Hierarchical tenant path")

    # role_ids is typically on the Read schema, as the assignments live in UserRole
    # Keeping it here for consistency with the provided code, but it's often omitted in Base/Create.
    role_ids: List[UUID] = Field(default_factory=list, description="IDs of roles assigned to user")

    @field_validator("tenant_path")
    @classmethod
    def validate_tenant_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate hierarchical tenant path format."""
        if v and not re.match(r"^[a-zA-Z0-9]+(/[a-zA-Z0-9]+)*$", v):
            raise ValueError("tenant_path must be in format 'org/tenant/subtenant'")
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=12, max_length=128, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Ensure password meets strong security requirements."""
        # ... validation logic remains the same ...
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one digit")
        if not re.search(r"[!@#$%^&*()_+]", value):
            raise ValueError("Password must include at least one special character")
        return value


class UserUpdate(BaseModel):
    """Schema for updating an existing user (PATCH semantics)."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, description="New full name")
    is_active: Optional[bool] = None
    status: Optional[UserStatus] = None

    # 🔑 FIX: Remove redundant tenant_id from update
    # The tenant_id of a user is usually immutable or
    # changed via a dedicated tenant service endpoint.
    # We keep tenant_path for potential updates to the hierarchy.
    # tenant_id: Optional[UUID] = None

    tenant_path: Optional[str] = None
    role_ids: Optional[List[UUID]] = None

    # Re-use the tenant path validator logic
    _validate_tenant_path = field_validator("tenant_path", mode="before")(
        UserBase.validate_tenant_path
    )


class UserRead(UserBase, ORMBaseSchema):
    """Schema for reading user information with ID, audit fields, and derived data."""

    id: UUID = Field(..., description="Unique user identifier")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    mfa_verified: Optional[bool] = Field(None, description="Whether MFA was verified")
    effective_permission_ids: List[UUID] = Field(
        default_factory=list,
        description="Aggregated permissions from all roles for RBAC enforcement",
    )
    # The inherited ORMBaseSchema now includes: created_at,
    #  updated_at, deleted_at, tenant_id, created_by, updated_by


class UserInDB(UserRead):
    """
    🔑 NEW: Schema representing the user model as it appears in the database.

    Includes the sensitive password hash for ORM loading.
    """

    password_hash: str = Field(..., description="The stored password hash")
    security_stamp: UUID = Field(..., description="Unique stamp updated on password change")


__all__ = ["UserStatus", "UserBase", "UserCreate", "UserUpdate", "UserRead", "UserInDB"]
