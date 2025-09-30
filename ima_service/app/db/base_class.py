"""SQLAlchemy base and timestamp mixin for all models."""

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
    """Adds `created_at` and `updated_at` timestamps to a model."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    )
