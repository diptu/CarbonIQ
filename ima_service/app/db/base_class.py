"""SQLAlchemy base class and timestamp mixin for all ORM models.

Includes:
- Declarative Base
- TimestampMixin with created_at and updated_at columns
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, text

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

    Columns
    -------
    created_at : DateTime
        Time when the record was created.
    updated_at : DateTime
        Time when the record was last updated; auto-updates on modification.
    """

    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()")
    )
