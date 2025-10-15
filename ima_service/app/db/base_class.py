"""SQLAlchemy declarative base for IMA service.

Includes:
- Declarative Base
- Optional TimestampMixin for convenience
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, text


# -------------------------
# Declarative Base
# -------------------------
class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# -------------------------
# Timestamp mixin (optional)
# -------------------------
class TimestampMixin:
    """Adds `created_at` and `updated_at` timestamps to a model."""

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
    )
