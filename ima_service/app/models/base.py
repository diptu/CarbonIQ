"""Base ORM model with common timestamp fields for all models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Base class for ORM models with timestamps."""

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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def touch(self) -> None:
        """Update `updated_at` timestamp to current UTC."""
        self.updated_at = datetime.utcnow()
