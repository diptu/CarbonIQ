"""Base Pydantic schemas for common ORM-backed fields."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ORMBaseSchema(BaseModel):
    """Base schema for ORM-backed entities.

    Notes
    -----
    - Includes timestamp fields shared by most models.
    - Provides model configuration enabling ORM conversion.
    - Used as a mixin for `*Read` and `*InDB` schemas.

    Attributes
    ----------
    created_at : datetime
        Timestamp when record was created.
    updated_at : datetime
        Timestamp of last modification.
    """

    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "extra": "ignore",
    }


__all__ = ["ORMBaseSchema"]
