# ima_service/app/models/role.py
"""Role model for the RBAC system."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User
# -----------------------------------------------


class Role(BaseModel):
    """Role defines a set of permissions for a tenant or system."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    label: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tenants.id"), nullable=True
    )
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships (Lines 24 and 27 are correct with string literals)
    users: Mapped[list["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role {self.name} ({self.label})>"
