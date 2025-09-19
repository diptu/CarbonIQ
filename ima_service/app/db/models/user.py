# FILE: ima_service/app/db/models/user.py
"""SQLAlchemy model for User (async-friendly, 2.0 style)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from ima_service.app.db.base import Base
from ima_service.app.domain.users.enums import UserGender, UserRole
from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gender: Mapped[UserGender] = mapped_column(
        SAEnum(UserGender, native_enum=False),
        default=UserGender.UNSPECIFIED,
        nullable=False,
    )

    # Authz
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False),
        default=UserRole.USER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_users_created_at", "created_at"),)

    def __repr__(self) -> str:  # pragma: no cover
        # keep it brief to satisfy line-length checks
        return (
            f"<User id={self.id} email={self.email!r} "
            f"role={self.role.name} gender={self.gender.name}>"
        )
