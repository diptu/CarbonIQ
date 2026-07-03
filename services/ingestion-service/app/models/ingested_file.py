"""The `ingested_files` table: one row per uploaded file, tenant-scoped.

This service owns this table exclusively (database-per-service). Downstream
services (ocr-service, energy-data-service, ...) receive a dispatch
notification rather than reading this table directly.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class FileType(str, enum.Enum):
    BILL_PDF = "bill_pdf"
    BILL_IMAGE = "bill_image"
    NEM12_CSV = "nem12_csv"
    REC_CERTIFICATE = "rec_certificate"
    LGC_CERTIFICATE = "lgc_certificate"
    PPA_CONTRACT = "ppa_contract"


class IngestionStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    VALIDATION_FAILED = "validation_failed"
    DISPATCHING = "dispatching"
    DISPATCHED = "dispatched"
    DISPATCH_FAILED = "dispatch_failed"


class IngestedFile(Base):
    __tablename__ = "ingested_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Tenant scoping (tenant-service is the source of truth for tenant_id itself;
    # this service only stores the claim it was given at upload time).
    tenant_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(nullable=False)

    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="file_type"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    storage_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, name="ingestion_status"),
        nullable=False,
        default=IngestionStatus.PENDING,
        index=True,
    )
    validation_errors: Mapped[list[str] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    dispatched_to: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
