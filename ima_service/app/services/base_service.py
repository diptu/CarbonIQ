from __future__ import annotations

from abc import ABC
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Optional, TypeVar, Generic, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from .audit_adapter import AuditAdapter

T = TypeVar("T")


class BaseService(AuditAdapter, Generic[T], ABC):
    """
    Base service providing tenant context, async DB session,
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
        super().__init__(audit_callable=getattr(audit_adapter, "_audit_callable", None))
        self.db: AsyncSession = db
        self.tenant_id: Optional[str] = tenant_id
        self.actor_id: Optional[str] = actor_id

    # --------------------------- TRANSACTION UTILS ---------------------------

    @asynccontextmanager
    async def transaction(self) -> Any:
        """Async context manager for DB transactions."""
        async with self.db.begin():
            try:
                yield
            except Exception:
                raise  # rollback is automatic on exception

    @classmethod
    def transactional(
        cls, func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None
    ) -> Callable[..., Any]:
        """
        Decorator for wrapping service methods in a DB transaction.
        Usage:
            @CRUDService.transactional
            async def my_method(...):
                ...
        """

        def decorator(inner_func: Callable[..., Coroutine[Any, Any, Any]]):
            @wraps(inner_func)
            async def wrapper(self: BaseService, *args, **kwargs):
                async with self.transaction():
                    return await inner_func(self, *args, **kwargs)

            return wrapper

        if func:
            return decorator(func)
        return decorator

    # ----------------------------- AUDIT UTILS -------------------------------

    async def _audit(
        self,
        action: str,
        resource: str,
        status: int,
        meta: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an audit event with tenant and actor context."""
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
        return self.actor_id

    @property
    def current_tenant_id(self) -> Optional[str]:
        return self.tenant_id

    # ---------------------------- QUERY SCOPING ------------------------------

    def scope_query(self, query: Select) -> Select:
        """
        Apply tenant_id scoping to a SQLAlchemy query.
        Assumes the first entity has a `tenant_id` column.
        """
        if self.tenant_id is None:
            raise ValueError("Tenant context is required for scoped queries.")

        entity = query.column_descriptions[0]["entity"]
        if not hasattr(entity, "tenant_id"):
            raise AttributeError(f"{entity} has no 'tenant_id' column")

        return query.where(entity.tenant_id == self.tenant_id)
