"""This schema validates incoming events from Kafka:"""

from typing import List

from pydantic import BaseModel


class RawFileEvent(BaseModel):
    file_id: str
    tenant_id: str | None = None
    org_id: str | None = None
    file_bytes: List[int]  # byte array
    file_type: str | None = "image"  # "pdf", "image", "csv"
