# app/services/reporting_service.py
from __future__ import annotations
from typing import Any, Type, Optional, Callable, Coroutine
from sqlalchemy import select

from .base_service import BaseService
from .rbac_service import RBACService

T = Any  # Generic ORM model placeholder


class ReportingService(BaseService[T]):
    """
    Tenant-scoped, RBAC-checked, audit-logged reporting service.
    Provides read/write operations with automatic audit and permission enforcement.
    """

    def __init__(self, rbac_service: RBACService, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rbac_service = rbac_service

    # ---------------------- PERMISSION CHECKS ----------------------

    async def _pre_check(self, permission: str) -> None:
        """Verify user has the required permission for the tenant context."""
        await self.rbac_service.check_access(
            self.current_user_id, permission, self.current_tenant_id
        )

    # ---------------------- GENERIC EXECUTOR WITH AUDIT ----------------------

    async def _execute(
        self, action: str, resource: str, db_op: Callable[[], Coroutine[Any, Any, Any]]
    ) -> Any:
        """Run a DB operation with RBAC pre-check and audit logging."""
        await self._pre_check(action)
        status = 200
        try:
            return await db_op()
        except Exception as e:
            status = 500
            raise
        finally:
            await self._audit(
                action=action,
                resource=resource,
                status=status,
                meta={"user_id": self.current_user_id},
            )

    # ---------------------- CRUD-LIKE OPERATIONS ----------------------

    async def list(self, model: Type[T], limit: int = 100, offset: int = 0) -> list[T]:
        """List all objects of a model with tenant scoping and audit."""

        async def op():
            stmt = self.scope_query(select(model)).limit(limit).offset(offset)
            result = await self.db.execute(stmt)
            return result.scalars().all()

        return await self._execute("report:list", model.__name__, op)

    async def get_by_id(self, model: Type[T], obj_id: str) -> Optional[T]:
        """Get a single object by ID with tenant scoping and audit."""

        async def op():
            stmt = self.scope_query(select(model).where(model.id == obj_id))
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        return await self._execute("report:view", model.__name__, op)

    async def update(self, obj: T) -> T:
        """Update an object in a transaction with audit logging."""

        async def op():
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return obj

        status = 200
        try:
            await self._pre_check("report:update")
            async with self.transaction():
                return await op()
        except Exception as e:
            status = 500
            raise
        finally:
            await self._audit(
                action="report:update",
                resource=type(obj).__name__,
                status=status,
                meta={"user_id": self.current_user_id},
            )
