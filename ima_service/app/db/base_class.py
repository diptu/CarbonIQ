from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base

# -------------------------
# Declarative base
# -------------------------
Base = declarative_base()


# -------------------------
# Timestamp mixin
# -------------------------
# pylint: disable=too-few-public-methods
class TimestampMixin:
    """Adds `created_at` and `updated_at` timestamps to a model.

    Attributes
    ----------
    created_at : DateTime
        Time when the record was created.
    updated_at : DateTime
        Time when the record was last updated; auto-updates on modification.
    """

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase


# -------------------------
# Declarative base
# -------------------------
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# -------------------------
# Timestamp mixin
# -------------------------
# pylint: disable=too-few-public-methods
class TimestampMixin:
    """Adds created_at and updated_at timestamps to a model.

    Attributes
    ----------
    created_at : datetime
        Time when the record was created.
    updated_at : datetime
        Time when the record was last updated; auto-updates on change.
    """

    created_at: datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
