# app/schemas/base.py
from datetime import datetime
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "extra": "forbid",
        "from_attributes": True,  # Pydantic V2 ORM mode
    }
