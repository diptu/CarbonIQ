# app/models/base.py
"""Base ORM model and common fields for IMA service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

import sqlalchemy as sa
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session

from ..db.base_class import Base
from .tenant_mixin import TenantMixin

if TYPE_CHECKING:
    from .user import User


class BaseModel(Base, TenantMixin):
    """
    Base class for ORM models with:
    - Timestamps: created_at, updated_at
    - Soft delete: deleted_at
    - Tenant-aware filtering: tenant_id
    - Audit fields: created_by, updated_by
    """

    __abstract__ = True  # <-- THIS prevents SQLAlchemy from mapping it as a table
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),  # type: ignore
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),  # type: ignore
        server_onupdate=sa.func.now(),  # type: ignore
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID who created the record",
    )

    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID who last updated the record",
    )

    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # -------------------------
    # Helper methods
    # -------------------------
    def touch(self) -> None:
        """Update the 'updated_at' timestamp to current UTC."""
        self.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Mark this record as deleted (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.touch()

    @classmethod
    def active(cls, session: Session):
        """
        Return only non-deleted records.

        Parameters
        ----------
        session : Session
            SQLAlchemy session to query.

        Returns
        -------
        Query
            Query filtered by `deleted_at IS NULL`.
        """
        return session.query(cls).filter(cls.deleted_at.is_(None))
