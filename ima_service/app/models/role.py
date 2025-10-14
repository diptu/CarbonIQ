"""Role model for RBAC system with hierarchical tenant support and effective permissions."""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User


class RoleStatus(str, Enum):
    """Enumeration for role status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Role(BaseModel):
    """
    Role defines a set of permissions for a tenant or system.
    Supports optional hierarchical inheritance via parent_role_id.

    Attributes
    ----------
    id : UUID
        Unique role identifier.
    name : str
        Role name (e.g., 'tenant_admin').
    description : Optional[str]
        Human-readable description of the role.
    priority : int
        Priority of the role (higher = more precedence).
    is_system_role : bool
        If True, accessible across all tenants.
    status : RoleStatus
        Role status (ACTIVE, INACTIVE, PENDING).
    parent_role_id : Optional[UUID]
        Parent role ID for hierarchical inheritance.
    children : List[Role]
        Child roles inheriting from this role.
    permissions : List[Permission]
        Permissions assigned directly to this role.
    users : List[User]
        Users assigned to this role.
    """

    __table_args__ = (
        Index("ix_roles_tenant_id", "tenant_id"),
        Index("ix_roles_system_role", "is_system_role"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[RoleStatus] = mapped_column(
        SAEnum(RoleStatus), default=RoleStatus.ACTIVE, nullable=False
    )

    parent_role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("roles.id"), nullable=True
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )
    children: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="parent",
        cascade="all, delete-orphan",
        remote_side=[id],
    )
    parent: Mapped[Optional["Role"]] = relationship(
        "Role", back_populates="children", remote_side=[parent_role_id]
    )

    def __repr__(self) -> str:
        return f"<Role {self.name} ({self.priority}) status={self.status.value}>"

    def effective_permissions(self) -> List["Permission"]:
        """
        Compute the effective permissions for this role including inherited permissions.

        Returns
        -------
        List[Permission]
            Permissions assigned to this role and inherited from parent roles.
        """
        perms = set(self.permissions)
        parent = self.parent
        visited = set()
        while parent and parent.id not in visited:
            perms.update(parent.permissions)
            visited.add(parent.id)
            parent = parent.parent
        return list(perms)
