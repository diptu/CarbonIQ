"""UserRole association table for RBAC system linking Users to Roles."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User  # type: ignore
    from .role import Role  # type: ignore


class UserRole(BaseModel):
    """
    Many-to-many relationship table linking Users to Roles.

    Inherits all audit fields (created_at, created_by, etc.) from BaseModel.

    Parameters
    ----------
    user_id : UUID
        Foreign key referencing `users.id`.
    role_id : UUID
        Foreign key referencing `roles.id`.
    tenant_id : Optional[UUID]
        Optional tenant context for hierarchical multi-tenancy.
    """

    __tablename__ = "user_roles"  # 🔑 Added explicit tablename

    __table_args__ = (
        Index("ix_user_roles_user_id", "user_id"),
        Index("ix_user_roles_role_id", "role_id"),
        Index("ix_user_roles_tenant_id", "tenant_id"),
    )

    # 🔑 FIX: Added ondelete="CASCADE" for automatic cleanup
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # 🔑 FIX: Added ondelete="CASCADE" for automatic cleanup
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    def __repr__(self) -> str:
        return f"<UserRole user={self.user_id} role={self.role_id} tenant={self.tenant_id}>"
