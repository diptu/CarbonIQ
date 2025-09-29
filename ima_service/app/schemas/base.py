"""
Base schemas for Pydantic models.

Includes:
- ORMBase: base for ORM integration
- PaginatedResponse: generic pagination
- APIResponse: standardized CRUD response envelope
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


# ----------------------
# Base ORM schema
# ----------------------
class ORMBase(BaseModel):
    """Base schema for Pydantic models with ORM support."""

    model_config = {
        "from_attributes": True,
        "alias_generator": lambda string: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(string.split("_"))
        ),
        "populate_by_name": True,
    }


# ----------------------
# Paginated response
# ----------------------
class PaginatedResponse(Generic[T], ORMBase):
    """Generic schema for paginated API responses."""

    total: int = Field(..., description="Total number of items available")
    skip: int = Field(..., description="Number of items skipped (offset)")
    limit: int = Field(..., description="Maximum number of items returned")
    previousPage: Optional[str] = None
    nextPage: Optional[str] = None
    firstPage: Optional[str] = None
    lastPage: Optional[str] = None
    items: List[T] = Field(..., description="List of items on this page")


# ----------------------
# Standard API response envelope
# ----------------------
class APIResponse(Generic[T], ORMBase):
    """
    Standardized API response envelope.

    Generic `details` can be any payload, including:
    - single object
    - list of objects
    - PaginatedResponse for paginated results
    """

    statusCode: int = Field(..., description="HTTP status code")
    msg: str = Field(..., description="Short descriptive message")
    details: Optional[T] = Field(None, description="Response payload")
