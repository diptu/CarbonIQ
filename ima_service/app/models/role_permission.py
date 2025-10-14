"""RolePermission association table for RBAC system with multi-tenant support."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

if TYPE_CHECKING:
    from .role import Role  # type: ignore
    from .permission import Permission  # type: ignore


class RolePermission(BaseModel):
    """
    Many-to-many relationship: Role <-> Permission.

    Inherits all audit fields (created_at, created_by, etc.) from BaseModel.
    """

    __tablename__ = "role_permissions"

    __table_args__ = (
        Index("ix_role_permissions_role_id", "role_id"),
        Index("ix_role_permissions_permission_id", "permission_id"),
        Index("ix_role_permissions_tenant_id", "tenant_id"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(String(36), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<RolePermission role={self.role_id} "
            f"permission={self.permission_id} tenant={self.tenant_id}>"
        )
