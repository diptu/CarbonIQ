# app/models/user_permissions.py
"""UserPermission association model."""

from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_class import Base

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission


class UserPermission(Base):
    """Association of users to permissions (direct assignment)."""

    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permission"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="users"
    )

    def __repr__(self) -> str:
        return f"<UserPermission user={self.user_id} permission={self.permission_id}>"
