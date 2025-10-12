"""Base service providing audit and tenant context for derived services."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Optional, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

from .audit_adapter import AuditAdapter

T = TypeVar("T")


class BaseService(AuditAdapter, Generic[T]):
    """
    Base service providing tenant context, database session,
    and audit logging for all derived services.
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        audit_adapter: Optional[AuditAdapter] = None,
    ) -> None:
        """
        Initialize the BaseService.

        Parameters
        ----------
        db : AsyncSession
            The async SQLAlchemy session.
        tenant_id : Optional[str]
            Tenant context for the service.
        actor_id : Optional[str]
            Actor (user) performing the actions.
        audit_adapter : Optional[AuditAdapter]
            Optional AuditAdapter to handle audit events.
        """
        super().__init__(
            audit_callable=audit_adapter._audit_callable if audit_adapter else None
        )
        self.db: AsyncSession = db
        self.tenant_id: Optional[str] = tenant_id
        self.actor_id: Optional[str] = actor_id

    @asynccontextmanager
    async def transaction(self) -> Any:
        """
        Async context manager for database transactions.

        Usage:
            async with service.transaction():
                await service.db.execute(...)
        """
        async with self.db.begin():
            try:
                yield
            except Exception:
                await self.db.rollback()
                raise
            await self.db.commit()

    async def _audit(
        self,
        action: str,
        resource: str,
        status: int,
        meta: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Helper to log an audit event with tenant and actor context.

        Parameters
        ----------
        action : str
            Action performed (e.g., "create", "update").
        resource : str
            Resource acted upon.
        status : int
            Status code of the action.
        meta : Optional[dict[str, Any]]
            Optional additional metadata.
        """
        await self.log(
            actor_id=self.actor_id,
            tenant_id=self.tenant_id,
            action=action,
            resource=resource,
            status=status,
            meta=meta or {},
        )
