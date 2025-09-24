"""Pydantic schemas base module.

This defines the base schema class that all other schemas will inherit from.
"""

from pydantic import BaseModel


class SchemaBase(BaseModel):
    """Base schema with common configuration for all Pydantic models."""

    class Config:
        """Pydantic configuration for all schemas."""

        from_attributes = True  # allow ORM conversion
        arbitrary_types_allowed = True
        populate_by_name = True


"""
Schemas package for ima_service.
Expose all pydantic models here for easy imports.
"""

from ima_service.app.schemas import user

__all__ = ["user"]
