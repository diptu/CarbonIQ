"""Role model definition."""

from __future__ import annotations

import uuid
from functools import cached_property
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, ForeignKey, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_class import Base

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User
    from .tenants import Tenant


class Role(Base):
    """Role model supporting hierarchical RBAC."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False, index=True
    )
    label: Mapped[int] = mapped_column(Integer, nullable=False)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    parent: Mapped[Optional["Role"]] = relationship(
        "Role", remote_side=[id], backref="sub_roles"
    )
    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )

    def get_hierarchy_path(self) -> List[str]:
        path = []
        current: Optional["Role"] = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return path

    def get_all_descendants(self) -> List["Role"]:
        descendants: List["Role"] = []

        def _collect_children(role: "Role") -> None:
            for child in role.sub_roles:
                descendants.append(child)
                _collect_children(child)

        _collect_children(self)
        return descendants

    @cached_property
    def all_descendants(self) -> List["Role"]:
        return self.get_all_descendants()

    def has_permission(self, permission_name: str) -> bool:
        current: Optional["Role"] = self
        while current:
            if any(p.name == permission_name for p in current.permissions):
                return True
            current = current.parent
        return False

    def to_tree(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "is_system": self.is_system,
            "label": self.label,
            "sub_roles": [child.to_tree() for child in self.sub_roles],
        }

    def __repr__(self) -> str:
        return f"<Role {self.name} (id={self.id})>"


@event.listens_for(Role, "before_insert")
@event.listens_for(Role, "before_update")
def prevent_cycles(mapper, connection, target: "Role") -> None:
    current = target.parent
    while current:
        if current.id == target.id:
            raise ValueError("Role cannot be its own ancestor.")
        current = current.parent
