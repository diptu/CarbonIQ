from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from shared_service.app.models.enums import PlanEnum, StatusEnum


# -----------------------------
# Base Schema
# -----------------------------
class TenantBase(BaseModel):
    """Common fields shared by all Tenant schemas."""

    name: str = Field(
        ..., max_length=255, description="Display name of the tenant/organization."
    )
    parent_id: Optional[UUID] = None

    status: Optional[StatusEnum] = Field(
        default=StatusEnum.ACTIVE, description="Current status of the tenant."
    )
    plan: Optional[PlanEnum] = Field(
        default=PlanEnum.FREE, description="Current subscription plan."
    )

    # ✅ normalize name to lowercase
    @field_validator("name", mode="before")
    def normalize_name(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()  # removes whitespace + lowercase
        return v

    @field_validator("status", "plan", mode="before")
    def normalize_enum(cls, v):
        return v.upper() if isinstance(v, str) else v


# -----------------------------
# Create Schema
# -----------------------------
class TenantCreate(TenantBase):
    """Used when creating a new tenant."""


# -----------------------------
# Update Schema
# -----------------------------
class TenantUpdate(BaseModel):
    """Used when updating tenant details."""

    name: Optional[str] = Field(None, max_length=255)
    status: Optional[StatusEnum] = None
    plan: Optional[PlanEnum] = None


# -----------------------------
# Response Schema
# -----------------------------
class TenantRead(TenantBase):
    """Tenant data returned to clients."""

    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # works like orm_mode=True in Pydantic v2
