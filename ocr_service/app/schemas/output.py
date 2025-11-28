"""This schema ensures OCR messages have a fixed shape"""

from pydantic import BaseModel


class OCRCompletedEvent(BaseModel):
    file_id: str
    tenant_id: str | None = None
    org_id: str | None = None
    ocr_text: str
