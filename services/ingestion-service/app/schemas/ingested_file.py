"""Pydantic v2 request/response schemas for the uploads API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.ingested_file import FileType, IngestionStatus


class IngestedFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    uploaded_by: uuid.UUID
    file_type: FileType
    original_filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
    status: IngestionStatus
    validation_errors: list[str] | None = None
    dispatched_to: str | None = None
    created_at: datetime
    updated_at: datetime


class IngestedFilePage(BaseModel):
    items: list[IngestedFileRead]
    page: int
    size: int
    total: int
