# app/models/permission.py
import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base, TimestampMixin
from .role import Role
from .role_permission import RolePermission


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), default=None)

    # Relationships
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"
