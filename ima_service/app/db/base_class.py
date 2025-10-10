# app/db/base_class.py
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class TimestampMixin:
    """
    Mixin that provides created_at / updated_at columns.

    Uses SQLAlchemy 2.0 mapped annotations to avoid
    MappedAnnotationError from older styles.
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


def uuid_pk_column() -> Any:
    """
    Return a mapped_column definition for a UUID PK.

    Use this helper in models for a consistent UUID PK column.
    Example:
        id: Mapped[uuid.UUID] = uuid_pk_column()
    """
    return mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
