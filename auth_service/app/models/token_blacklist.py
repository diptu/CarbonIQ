"""SQLAlchemy model for storing blacklisted JWT tokens."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from auth_service.app.db.session import engine


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Base class for SQLAlchemy models."""


class TokenBlacklist(Base):  # pylint: disable=too-few-public-methods
    """Table to store blacklisted JWT tokens."""

    __tablename__ = "token_blacklist"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key: unique identifier for each blacklist record",
    )

    jti: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        comment="JWT ID (jti) of the blacklisted token",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        comment="Timestamp when the token was blacklisted",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
        comment="Timestamp when the token record was last updated",
    )


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
