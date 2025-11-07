# user_service/app/models/user.py
from __future__ import annotations

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from user_service.app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # --- Relationships ---
    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # cached properties
    @property
    def roles_cached(self) -> list[str]:
        return sorted({ur.role.name for ur in self.roles if ur.role})

    @property
    def permissions_cached(self) -> list[str]:
        perms = set()
        for ur in self.roles:
            for p in ur.role.permissions:
                perms.add(p.name)
        return sorted(perms)

    def __repr__(self):
        return f"<User(email={self.email!r}, active={self.is_active})>"
