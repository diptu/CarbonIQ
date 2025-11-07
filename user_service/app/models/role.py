# user_service/app/models/role.py
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from user_service.app.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    users = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(name={self.name})>"
