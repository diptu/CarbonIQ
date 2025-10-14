"""Base ORM model and common fields for IMA service.

Provides:
- BaseModel: common timestamp fields and tenant scoping.
- touch() method for updated_at.
- Integrates TenantMixin for tenant-aware queries.
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func  # ✅ important
from .tenant_mixin import TenantMixin


class BaseModel(DeclarativeBase, TenantMixin):
    """Base class for ORM models with timestamps and optional tenant scoping."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=E1102
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=E1102
        server_onupdate=func.now(),  # pylint: disable=E1102
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
