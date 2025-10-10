from __future__ import annotations
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseService(Generic[T]):
    """Core base service for async SQLAlchemy models."""

    def __init__(self, db: AsyncSession):
        self.db = db


# Optional logging decorators
def log_method_call(func):
    async def wrapper(*args, **kwargs):
        # You can implement logging here
        return await func(*args, **kwargs)

    return wrapper


def log_action(event_name: str, metadata: dict, tenant_id: str | None = None):
    # Simple log placeholder
    print(f"[ACTION] {event_name} | tenant={tenant_id} | metadata={metadata}")
