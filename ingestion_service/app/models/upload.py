# ingestion_service/app/models/upload.py

import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


# pylint: disable=too-few-public-methods, not-callable
class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Primary key UUID for the upload",
    )
    filename = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Original uploaded file name",
    )
    content_type = Column(
        String(255),
        nullable=True,
        comment="MIME type of the file",
    )
    path = Column(
        String(255),
        nullable=True,
        comment="Filesystem or S3 path to the file",
    )
    size = Column(
        Integer,
        nullable=True,
        comment="File size in bytes",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Upload creation timestamp",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Upload last updated timestamp",
    )

    @property
    def size_mb(self) -> float:
        """Return file size in megabytes (MB)."""
        return round(self.size / (1024 * 1024), 2)

    def __repr__(self) -> str:
        return (
            f"<Upload(id={self.id}, filename={self.filename}, path={self.path}, size={self.size})>"
        )
