"""Permission model for the RBAC system with optional tenant scoping."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, Query

from .base import BaseModel

from .role_permission import RolePermission

if TYPE_CHECKING:
    from .role import Role  # noqa: F401


class Permission(BaseModel):
    """
    Represents a specific action or resource access right in the system.

    (Docstring content remains the same, but now implicitly includes created_by/updated_by
    from BaseModel.)
    """

    __table_args__ = (
        Index("ix_permissions_code", "code"),
        Index("ix_permissions_module", "module"),
        Index("ix_permissions_tenant_id", "tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(String(36), nullable=True)
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=RolePermission.__table__,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission code={self.code} name={self.name}>"

    @classmethod
    def for_module(cls, session: Session, module: str, tenant_id: Optional[str] = None) -> Query:
        """
        Return permissions filtered by module and optionally by tenant_id.

        (Docstring remains the same)
        """
        query = cls.for_tenant(session, tenant_id) if tenant_id else session.query(cls)
        return query.filter(cls.module == module)
