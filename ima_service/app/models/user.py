"""User model for multi-tenant RBAC system with hierarchical tenant support."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Boolean, String, Text, Index, DateTime, Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from ..core.security import hash_password, verify_password

from .user_role import UserRole

if TYPE_CHECKING:
    from .role import Role


class UserStatus(str, Enum):
    """Enum representing user account status."""

    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"


class User(BaseModel):
    """
    Represents an authenticated individual tied to a tenant in a hierarchical
    multi-tenant SaaS application.
    """

    __table_args__ = (
        Index("ix_users_tenant_id", "tenant_id"),
        Index("ix_users_email", "email"),
        Index("ix_users_tenant_active", "tenant_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    security_stamp: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, nullable=False)
    tenant_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=UserRole.__table__, back_populates="users"
    )

    def __repr__(self) -> str:
        """Return a string representation of the user."""
        return f"<User {self.email} status={self.status}>"

    @hybrid_property
    def password(self) -> str:
        """Prevent direct reading of the password hash."""
        raise AttributeError("Password is not readable")

    @password.setter  # type:ignore[no-redef]
    def password(self, password: str) -> None:
        """
        Hash the given password and update the security stamp.
        """
        self.password_hash = hash_password(password)
        self.security_stamp = uuid.uuid4()

    def verify_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the stored hash.
        """
        return verify_password(password, self.password_hash)

    def activate(self) -> None:
        """Activate the user account and update timestamps."""
        self.is_active = True
        self.status = UserStatus.ACTIVE
        self.touch()

    def deactivate(self) -> None:
        """Deactivate the user account and update timestamps."""
        self.is_active = False
        self.status = UserStatus.BLOCKED
        self.touch()

    def mark_login(self) -> None:
        """Update the last login timestamp to current UTC."""
        self.last_login_at = datetime.utcnow()
        self.touch()
