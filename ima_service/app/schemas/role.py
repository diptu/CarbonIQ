"""
Schemas for role management.

Includes role creation, reading, and standardized API response envelope.
"""

from enum import Enum
from typing import Optional
from uuid import UUID

from .base import ORMBase, PaginatedResponse


# ----------------------
# Role enum
# ----------------------
class RoleName(str, Enum):
    """Enumeration of supported system roles."""

    BILLING_ADMIN = "BILLING_ADMIN"
    TENANT_ADMIN = "TENANT_ADMIN"
    VIEWER = "VIEWER"
    MEMBER = "MEMBER"


# ----------------------
# Base role schema
# ----------------------
class RoleBase(ORMBase):
    """Base schema for role attributes."""

    name: RoleName
    description: Optional[str] = None
    is_system: bool = False


# ----------------------
# Role creation schema
# ----------------------
class RoleCreate(RoleBase):
    """Schema for creating a new role."""


# ----------------------
# Role read schema
# ----------------------
class RoleRead(RoleBase):
    """Schema for returning a role with ID."""

    id: UUID


# ----------------------
# Paginated list of roles
# ----------------------
class RoleList(PaginatedResponse[RoleRead]):
    """Paginated response for listing roles."""


# ----------------------
# Standardized API response envelope
# ----------------------
class RoleListResponse(ORMBase):
    """Standardized API response envelope for role list."""

    statusCode: int
    msg: str
    details: RoleList
