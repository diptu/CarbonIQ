# app/services/base_service.py
from __future__ import annotations
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.audit_adapter import audit_adapter


class BaseService:
    """
    Base class for all services providing common utilities.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = (
            audit_adapter  # use audit_adapter.log_event via self.audit.log_event
        )

    async def commit(self) -> None:
        """Commit current DB transaction."""
        await self.db.commit()

    async def rollback(self) -> None:
        """Rollback current DB transaction."""
        await self.db.rollback()

    async def refresh(self, instance: Any) -> Any:
        """Refresh instance from DB."""
        await self.db.refresh(instance)
        return instance

    def log_action(self, action: str, extra: Optional[dict[str, Any]] = None):
        """Shortcut for audit decorator (can also wrap functions)."""
        return self.audit.log_event(action, extra)
