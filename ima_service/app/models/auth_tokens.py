# auth_tokens.py
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class AuthToken(BaseModel):
    __tablename__ = "auth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(Text, nullable=False)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    token_type: Mapped[str] = mapped_column(
        Enum("access", "refresh", "api_key", name="token_type_enum"),
        nullable=False,
        default="access",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="auth_tokens",
        foreign_keys=[user_id],
        lazy="joined",
    )

    __table_args__ = (
        Index("idx_auth_token_expires_at", "expires_at"),
        Index("idx_auth_token_jti", "jti"),
    )

    def revoke(self) -> None:
        self.revoked = True
        self.revoked_at = datetime.now(timezone.utc)
        self.touch()

    def is_active(self) -> bool:
        return not self.revoked and datetime.now(timezone.utc) < self.expires_at


class InvitationToken(BaseModel):
    __tablename__ = "invitation_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(
        String(36), nullable=False, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[str] = mapped_column(
        Enum("PENDING", "ACCEPTED", "REVOKED", name="invite_status_enum"),
        nullable=False,
        default="PENDING",
    )
    invited_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    inviter: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="invitations",
        foreign_keys=[invited_by_id],
        lazy="joined",
    )
