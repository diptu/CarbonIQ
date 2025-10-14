"""Permission model for the RBAC system with optional tenant scoping."""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .role import Role  # noqa: F401


class Permission(BaseModel):
    """
    Represents a specific action or resource access right in the system.

    Parameters
    ----------
    id : UUID
        Unique identifier for the permission.
    code : str
        Machine-readable permission code (e.g., 'manage_users').
    name : Optional[str]
        Human-friendly display name.
    description : Optional[str]
        Textual description of the permission.
    module : Optional[str]
        Logical grouping or module (e.g., 'user', 'tenant').
    roles : List[Role]
        Roles that include this permission.
    tenant_id : Optional[UUID]
        Optional tenant scope for multi-tenant isolation.
    created_at : datetime
        Timestamp when the permission was created.
    updated_at : datetime
        Timestamp when the permission was last updated.
    deleted_at : Optional[datetime]
        Soft-delete timestamp.
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

    # Multi-tenant awareness
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(String(36), nullable=True)

    # RBAC relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission code={self.code} name={self.name}>"

    @classmethod
    def for_module(cls, session, module: str, tenant_id: Optional[str] = None):
        """
        Return permissions filtered by module and optionally by tenant_id.

        Parameters
        ----------
        session : Session
            SQLAlchemy session.
        module : str
            Module name to filter permissions by.
        tenant_id : Optional[str]
            Tenant ID for scoping (optional).

        Returns
        -------
        Query
            SQLAlchemy Query object filtered by module (and tenant if given).
        """
        query = cls.for_tenant(session, tenant_id) if tenant_id else session.query(cls)
        return query.filter(cls.module == module)
