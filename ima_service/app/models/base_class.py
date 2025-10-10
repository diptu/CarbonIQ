"""Shared SQLAlchemy declarative base class.

Provides automatic timestamp columns (`created_at`, `updated_at`) for
all derived ORM models.

This module is designed to be:
- PEP 8 / pylint compliant (≤80 chars/line, snake_case)
- mypy compatible (full type hints)
- PyPy compatible (standard-library only)
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base ORM model.

    Notes
    -----
    Every subclass automatically includes timestamp columns that are
    populated in the database using `NOW()` defaults.

    Attributes
    ----------
    created_at : datetime
        Time (with timezone) when the record was first inserted.
    updated_at : datetime
        Time (with timezone) when the record was last updated.
    """

    # pylint: disable=too-few-public-methods
    __abstract__: ClassVar[bool] = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
        doc="Timestamp when the row was created.",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
        nullable=False,
        doc="Timestamp when the row was last updated.",
    )

    # Optionally: reusable helper to get dict view
    def to_dict(self) -> dict[str, datetime]:
        """
        Return timestamps as a serializable dictionary.

        Returns
        -------
        dict of str to datetime
            Keys: 'created_at', 'updated_at'.
        """
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
