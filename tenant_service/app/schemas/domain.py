from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Base schema (shared attributes)
# ---------------------------------------------------------
class TenantDomainBase(BaseModel):
    domain: str = Field(..., example="example.com")
    is_verified: bool = False


# ---------------------------------------------------------
# Create schema
# ---------------------------------------------------------
class TenantDomainCreate(TenantDomainBase):
    tenant_id: UUID


# ---------------------------------------------------------
# Update schema
# ---------------------------------------------------------
class TenantDomainUpdate(BaseModel):
    domain: str | None = Field(None, example="newdomain.com")
    is_verified: bool | None = None


# ---------------------------------------------------------
# Read schema (response)
# ---------------------------------------------------------
class TenantDomainRead(TenantDomainBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
