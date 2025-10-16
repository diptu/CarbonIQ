# user.py
from __future__ import annotations
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Boolean, String, Text, Index, DateTime, Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from ..core.security import hash_password, verify_password
from .user_role import UserRole


class UserStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"


class User(BaseModel):
    __tablename__ = "users"
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
    is_super_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    security_stamp: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, nullable=False)
    tenant_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Relationships ---
    roles = relationship(
        "Role",
        secondary=UserRole.__table__,
        back_populates="users",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="Role.id == UserRole.role_id",
    )

    auth_tokens: Mapped[list["AuthToken"]] = relationship(
        "AuthToken",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[AuthToken.user_id]",
    )

    invitations: Mapped[list["InvitationToken"]] = relationship(
        "InvitationToken",
        back_populates="inviter",
        cascade="all, delete-orphan",
        foreign_keys="[InvitationToken.invited_by_id]",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[AuditLog.user_id]",
    )

    @hybrid_property
    def password(self) -> str:
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = hash_password(password)
        self.security_stamp = uuid.uuid4()

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def activate(self) -> None:
        self.is_active = True
        self.status = UserStatus.ACTIVE
        self.touch()

    def deactivate(self) -> None:
        self.is_active = False
        self.status = UserStatus.BLOCKED
        self.touch()

    def mark_login(self) -> None:
        self.last_login_at = datetime.utcnow()
        self.touch()
