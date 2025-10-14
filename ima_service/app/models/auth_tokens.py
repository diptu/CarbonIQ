"""AuthToken model for managing user refresh/session tokens."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class AuthToken(BaseModel):
    """
    Represents a user authentication or session token.

    Inherits common fields (created_at, updated_at, tenant_id, created_by, updated_by)
    from BaseModel.
    """

    __tablename__ = "auth_tokens"

    # pylint: disable=unsubscriptable-object, not-callable

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    token: Mapped[str] = mapped_column(Text, nullable=False)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),  # pylint: disable=E1102
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    session_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    token_type: Mapped[str] = mapped_column(
        Enum("access", "refresh", "api_key", name="token_type_enum"),
        nullable=False,
        default="access",
    )

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    trace_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    mfa_verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="auth_tokens", lazy="joined")

    __table_args__ = (
        Index("idx_auth_token_expires_at", "expires_at"),
        Index("idx_auth_token_jti", "jti"),
        Index("idx_auth_token_revoked_user", "revoked", "user_id"),
    )

    # ==============================
    # Behavioral Methods
    # ==============================

    def revoke(self) -> None:
        """Revoke this token and mark revocation timestamp."""
        self.revoked = True
        self.revoked_at = datetime.now(timezone.utc)
        self.touch()

    def is_active(self) -> bool:
        """Return True if token is active and not expired."""
        return not self.revoked and datetime.now(timezone.utc) < self.expires_at

    def mark_used(self) -> None:
        """Mark this token as recently used."""
        self.last_used_at = datetime.now(timezone.utc)
        self.touch()

    def __repr__(self) -> str:
        return (
            f"<AuthToken user_id={self.user_id} "
            f"jti={self.jti} type={self.token_type} revoked={self.revoked}>"
        )
