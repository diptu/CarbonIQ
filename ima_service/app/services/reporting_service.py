"""Reporting service placeholder for IMA Service."""

from typing import Any, Optional
from .crud_service import CRUDService


class ReportingService(CRUDService[Any]):
    """Service for managing reporting operations (placeholder)."""

    async def list(
        self,
        model: type[Any],
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """
        List report entries.

        `model` is required to match CRUDService signature.
        """
        return await super().list(model=model, limit=limit, offset=offset)

    async def get_by_id(self, model: type[Any], obj_id: str) -> Optional[Any]:
        """Get a report entry by ID."""
        return await super().get_by_id(model=model, obj_id=obj_id)

    async def update(self, obj: Any) -> Any:
        """Update a report entry."""
        return await super().update(obj)
