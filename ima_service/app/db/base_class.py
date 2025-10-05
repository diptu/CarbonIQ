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
