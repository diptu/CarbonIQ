from typing import Optional

from pydantic import BaseModel

MAX_FILE_SIZE = 100 * 1024 * 1024  # Example: 100 MB in bytes, or import from settings


class UploadMetaIn(BaseModel):
    filename: str


class UploadMetaOut(BaseModel):
    id: str  # UUID as string
    filename: str
    content_type: Optional[str]
    size: int
    path: str  # Always return as string to avoid FastAPI Path serialization issues
    size_mb: Optional[float] = None
    # created_at: Optional[str] = None
    # updated_at: Optional[str] = None

    model_config = {
        "from_attributes": True,  # Pydantic v2 replacement for orm_mode
    }
