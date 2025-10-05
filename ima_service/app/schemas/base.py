"""
app.schemas.base.py
Base schemas for Pydantic models.

Includes:
- ORMBase: base for ORM integration
- PaginatedResponse: generic pagination
- APIResponse: standardized CRUD response envelope
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    """
    Base schema for Pydantic models with ORM support.

    Notes
    -----
    - Supports `from_attributes=True` for ORM integration.
    - Provides alias generator converting snake_case to camelCase.
    - Allows population by field name.
    """

    model_config = {
        "from_attributes": True,
        "alias_generator": lambda string: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(string.split("_"))
        ),
        "populate_by_name": True,
    }


class PaginatedResponse(Generic[T], ORMBase):
    """
    Generic schema for paginated API responses.

    Attributes
    ----------
    total : int
        Total number of items available.
    skip : int
        Number of items skipped (offset).
    limit : int
        Maximum number of items returned.
    previousPage : Optional[str]
        URL to the previous page, if any.
    nextPage : Optional[str]
        URL to the next page, if any.
    firstPage : Optional[str]
        URL to the first page.
    lastPage : Optional[str]
        URL to the last page.
    items : List[T]
        List of items on this page.
    """

    total: int = Field(..., description="Total number of items available")
    skip: int = Field(..., description="Number of items skipped (offset)")
    limit: int = Field(..., description="Maximum number of items returned")
    previousPage: Optional[str] = None
    nextPage: Optional[str] = None
    firstPage: Optional[str] = None
    lastPage: Optional[str] = None
    items: List[T] = Field(..., description="List of items on this page")


class APIResponse(Generic[T], ORMBase):
    """
    Standardized API response envelope.

    Attributes
    ----------
    statusCode : int
        HTTP status code of the response.
    msg : str
        Short descriptive message.
    details : Optional[T]
        Generic response payload; can be a single object,
        list of objects, or PaginatedResponse for paginated results.
    """

    statusCode: int = Field(..., description="HTTP status code")
    msg: str = Field(..., description="Short descriptive message")
    details: Optional[T] = Field(None, description="Response payload")
