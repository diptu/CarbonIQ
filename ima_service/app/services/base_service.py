# app/services/base_service.py
from __future__ import annotations

from abc import ABC
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Optional, TypeVar, Generic, Callable, Coroutine, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.audit_adapter import AuditAdapter

T = TypeVar("T")


class BaseService(AuditAdapter, Generic[T], ABC):
    """
    Base service providing:
      - Tenant and actor context
      - Async DB session with transaction helpers
      - Audit logging utilities
      - Tenant-scoped query support

    All derived services should inherit from this to enforce
    consistent transaction, audit, and multi-tenant behavior.
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        audit_adapter: Optional[AuditAdapter] = None,
    ) -> None:
        super().__init__(audit_callable=getattr(audit_adapter, "_audit_callable", None))
        self.db: AsyncSession = db
        self.tenant_id: Optional[str] = tenant_id
        self.actor_id: Optional[str] = actor_id

    # --------------------------- TRANSACTION UTILITIES ---------------------------

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """
        Async context manager for database transactions.
        Rolls back automatically on exception.
        Usage:
            async with service.transaction():
                ...
        """
        async with self.db.begin():
            try:
                yield
            except Exception:
                # Automatic rollback handled by SQLAlchemy async session
                raise

    @classmethod
    def transactional(
        cls, func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None
    ) -> Callable[..., Any]:
        """
        Decorator for wrapping service methods in a DB transaction.
        Usage:
            @BaseService.transactional
            async def my_method(...):
                ...
        """

        def decorator(inner_func: Callable[..., Coroutine[Any, Any, Any]]):
            @wraps(inner_func)
            async def wrapper(self: BaseService, *args, **kwargs):
                async with self.transaction():
                    return await inner_func(self, *args, **kwargs)

            return wrapper

        return decorator(func) if func else decorator

    # ----------------------------- AUDIT UTILITIES -------------------------------

    async def _audit(
        self,
        action: str,
        resource: str,
        status: int,
        meta: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log an audit event with tenant and actor context.

        Args:
            action (str): Action being performed.
            resource (str): Resource name (usually model or service name).
            status (int): HTTP-like status code.
            meta (Optional[dict]): Additional metadata for audit.
        """
        await self.log(
            actor_id=self.actor_id,
            tenant_id=self.tenant_id,
            action=action,
            resource=resource,
            status=status,
            meta=meta or {},
        )

    # -------------------------- CONTEXT PROPERTIES ---------------------------

    @property
    def current_user_id(self) -> Optional[str]:
        """Return current actor/user ID."""
        return self.actor_id

    @property
    def current_tenant_id(self) -> Optional[str]:
        """Return current tenant ID."""
        return self.tenant_id

    # ---------------------------- QUERY SCOPING ------------------------------

    def scope_query(self, query: Select) -> Select:
        """
        Apply tenant_id scoping to a SQLAlchemy Select query.

        Raises:
            ValueError: If tenant context is not set.
            AttributeError: If the model has no 'tenant_id' column.

        Returns:
            Select: SQLAlchemy query scoped to the tenant.
        """
        if self.tenant_id is None:
            raise ValueError("Tenant context is required for scoped queries.")

        entity = query.column_descriptions[0]["entity"]
        if not hasattr(entity, "tenant_id"):
            raise AttributeError(f"{entity} has no 'tenant_id' column")

        return query.where(entity.tenant_id == self.tenant_id)
