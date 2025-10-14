"""Base ORM model and common fields for IMA service."""

from __future__ import annotations  # For forward references like 'User'

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

# Import SQLAlchemy components explicitly to resolve Pylint E1102
import sqlalchemy as sa
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .tenant_mixin import TenantMixin

# Type checking import for relationships without circular import issues
if TYPE_CHECKING:
    from .user import User


class BaseModel(DeclarativeBase, TenantMixin):
    """
    Base class for ORM models with timestamps, full user-based audit fields,
    soft-delete, and optional tenant scoping.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),  # pylint: disable=E1102
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),  # pylint: disable=E1102
        server_onupdate=sa.func.now(),  # pylint: disable=E1102
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # 🔑 NEW: Tracks the user who created the record (Audit trail)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID who created the record",
    )

    # 🔑 NEW: Tracks the user who last updated the record (Audit trail)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID who last updated the record",
    )

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(String(36), nullable=True)

    def touch(self):
        """Update the 'updated_at' timestamp."""
        self.updated_at = datetime.utcnow()

    def soft_delete(self):
        """Mark this record as deleted (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.touch()

    @classmethod
    def active(cls, session):
        """Return only non-deleted records."""
        return session.query(cls).filter(cls.deleted_at.is_(None))
