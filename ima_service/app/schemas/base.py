"""Base Pydantic schemas for common ORM-backed fields, including tenant and soft-delete."""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ORMBaseSchema(BaseModel):
    """
    Base schema for ORM-backed entities, providing common audit, timestamp,
    and multi-tenancy fields.

    Notes
    -----
    - Includes full audit trail fields (created_by/updated_by).
    - Includes timestamp fields shared by most models.
    - Supports soft-delete (`deleted_at`) and optional tenant scoping (`tenant_id`).
    - Provides model configuration enabling ORM conversion.
    - Used as a mixin for `*Read` and `*InDB` schemas.

    Attributes
    ----------
    created_at : datetime
        Timestamp when record was created.
    updated_at : datetime
        Timestamp of last modification.
    created_by : Optional[UUID]
        User ID who created the record.
    updated_by : Optional[UUID]
        User ID who last updated the record.
    deleted_at : Optional[datetime]
        Soft-delete timestamp (None if active).
    tenant_id : Optional[UUID]
        Tenant context for multi-tenant models.
    """

    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # 🔑 Finalized Audit Fields
    created_by: Optional[UUID] = Field(None, description="User ID who created the record")
    updated_by: Optional[UUID] = Field(None, description="User ID who last updated the record")

    deleted_at: Optional[datetime] = Field(None, description="Soft-delete timestamp")
    tenant_id: Optional[UUID] = Field(None, description="Tenant context for multi-tenant models")

    model_config = {
        "from_attributes": True,
        "extra": "ignore",
    }


__all__ = ["ORMBaseSchema"]
