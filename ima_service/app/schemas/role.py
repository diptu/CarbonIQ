"""
Schemas for role management.

Includes role creation, reading, and standardized API response envelope.
"""

from typing import Optional, List
from uuid import UUID
from enum import Enum
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


# ----------------------
# Role creation schema
# ----------------------
class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    pass


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

    pass


# ----------------------
# Standardized API response envelope
# ----------------------
class RoleListResponse(ORMBase):
    """Standardized API response envelope for role list."""

    statusCode: int
    msg: str
    details: RoleList
