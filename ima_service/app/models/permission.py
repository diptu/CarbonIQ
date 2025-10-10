"""Permission model definition."""

from __future__ import annotations

import uuid
from functools import cached_property
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_class import Base

if TYPE_CHECKING:
    from .role import Role
    from .tenants import Tenant


class Permission(Base):
    """Permission model."""

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )
    # User direct permissions
    users: Mapped[List["UserPermission"]] = relationship(
        "UserPermission", back_populates="permission", cascade="all, delete-orphan"
    )

    @cached_property
    def assigned_roles(self) -> List["Role"]:
        return self.roles

    def __repr__(self) -> str:
        return f"<Permission {self.name} (id={self.id})>"
