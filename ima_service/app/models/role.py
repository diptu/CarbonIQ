# app/models/role.py
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base, TimestampMixin
from .permission import Permission
from .user_roles import UserRole


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), default=None)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole", back_populates="role", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
