from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    """
    Base schema for ORM models with Pydantic V2 support.
    """

    model_config = {
        "from_attributes": True,
        "alias_generator": lambda s: "".join(
            word.capitalize() if i > 0 else word for i, word in enumerate(s.split("_"))
        ),
        "populate_by_name": True,
    }


class PaginatedResponse(Generic[T], ORMBase):
    total: int = Field(..., description="Total items available")
    skip: int = Field(..., description="Number of items skipped (offset)")
    limit: int = Field(..., description="Maximum items returned")
    previousPage: Optional[str] = None
    nextPage: Optional[str] = None
    firstPage: Optional[str] = None
    lastPage: Optional[str] = None
    items: List[T] = Field(..., description="Items in this page")


class APIResponse(Generic[T], ORMBase):
    statusCode: int = Field(..., description="HTTP status code")
    msg: str = Field(..., description="Short descriptive message")
    details: Optional[T] = Field(None, description="Response payload")
