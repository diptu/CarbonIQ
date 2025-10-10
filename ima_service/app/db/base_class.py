# app/db/base_class.py
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


class TimestampMixin:
    """
    Mixin that provides created_at / updated_at columns.

    Uses SQLAlchemy 2.0 style mapped annotations to avoid the
    MappedAnnotationError raised when legacy annotations are present.
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Optional small helper if you want UUID primary key column in models
def uuid_pk_column() -> Any:
    """Return a mapped_column definition for a UUID primary key."""
    return mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
