"""Schemas for role management with DB-driven RBAC."""

from enum import Enum
from typing import List, Optional
from uuid import UUID
from .base import ORMBase, PaginatedResponse
from .permission import PermissionRead


class RoleName(str, Enum):
    """Enumeration of system roles."""

    TENANT_ADMIN = "TENANT_ADMIN"
    BILLING_ADMIN = "BILLING_ADMIN"
    VIEWER = "VIEWER"
    MEMBER = "MEMBER"


class RoleBase(ORMBase):
    """Base schema for role attributes."""

    name: RoleName
    level: int
    description: Optional[str] = None
    is_system: bool = False
    permissions: Optional[List[PermissionRead]] = []


class RoleCreate(ORMBase):
    """Schema for creating a new role."""

    name: RoleName
    level: int
    description: Optional[str] = None
    is_system: bool = False
    permissions: Optional[List[UUID]] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "TENANT_ADMIN",
                "level": 4,
                "description": "Role for tenant administrators",
                "is_system": False,
                "permissions": [],
            }
        }


class RoleUpdate(RoleBase):
    """Schema for updating a role."""


class RoleRead(RoleBase):
    """Schema for reading a role."""

    id: UUID


class RoleList(PaginatedResponse[RoleRead]):
    """Paginated response for roles."""

    pass


class RoleListResponse(ORMBase):
    """Standardized API response envelope for role list."""

    statusCode: int
    msg: str
    details: RoleList
