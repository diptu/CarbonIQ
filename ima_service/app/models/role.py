"""Role model for RBAC system with hierarchical tenant support and effective permissions."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .user_role import UserRole
from .role_permission import RolePermission

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
    """

    __tablename__ = "roles"

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
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    # inside Role model
    users = relationship(
        "User",
        secondary=UserRole.__table__,
        back_populates="roles",
        primaryjoin="Role.id == UserRole.role_id",
        secondaryjoin="User.id == UserRole.user_id",
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=RolePermission.__table__,
        back_populates="roles",
        lazy="selectin",
    )

    # Fix for hierarchical roles with delete-orphan
    children: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True,
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
        """
        perms = set(self.permissions)
        parent = self.parent
        visited = set()
        while parent and parent.id not in visited:
            perms.update(parent.permissions)
            visited.add(parent.id)
            parent = parent.parent
        return list(perms)
