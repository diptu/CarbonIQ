from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Base schema (shared attributes)
# ---------------------------------------------------------
class DomainBase(BaseModel):
    domain: str | None = Field(None, example="apple")
    is_verified: bool = False


# ---------------------------------------------------------
# Create schema
# ---------------------------------------------------------
class DomainCreate(DomainBase):
    tenant_id: UUID


# ---------------------------------------------------------
# Update schema
# ---------------------------------------------------------
class DomainUpdate(BaseModel):
    domain: str | None = Field(None, example="newdomain.com")
    is_verified: bool | None = None


# ---------------------------------------------------------
# Read schema (response)
# ---------------------------------------------------------
class DomainRead(DomainBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
