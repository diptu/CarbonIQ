# app/schemas/tenant.py
from __future__ import annotations
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    name: str = Field(..., description="Tenant name")
    domain: Optional[str] = Field(None, description="Tenant domain")
    schema_name: Optional[str] = Field(None, description="DB schema name")
    parent_id: Optional[UUID] = Field(None, description="Parent tenant ID")
    plan: Optional[str] = Field(None, description="Subscription plan")
    is_active: Optional[bool] = Field(True, description="Active status")
    metadata: Optional[dict] = Field(default_factory=dict)
    source: Optional[str] = Field("local", description="Source of tenant data")


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    schema_name: Optional[str] = None
    parent_id: Optional[UUID] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[dict] = None
    source: Optional[str] = None


class TenantRead(TenantBase):
    id: UUID
    external_id: Optional[UUID] = None
    version: int
    last_synced_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    parent: Optional[TenantRead] = None
    children: List[TenantRead] = []

    class Config:
        orm_mode = True
