# app/schemas.py
from typing import Optional

from ingestion_service.app.core.config import settings
from pydantic import BaseModel

MAX_FILE_SIZE = settings.MAX_FILE_SIZE * 1024 * 1024  # MAX_FILE_SIZE MB in bytes


class UploadMetaIn(BaseModel):
    filename: str


class UploadMetaOut(BaseModel):
    id: str  # UUID as string
    filename: str
    content_type: Optional[str]
    size: int
    path: str
    # created_at: datetime
    # updated_at: Optional[datetime] = None  # optional if you want to include

    class Config:
        orm_mode = True  # allows reading from SQLAlchemy ORM objects
