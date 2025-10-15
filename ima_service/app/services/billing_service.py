from __future__ import annotations
from typing import Any, Optional, Type
from sqlalchemy import select

from .base_service import BaseService
from .rbac_service import RBACService

T = Any  # Generic ORM model placeholder


class BillingService(BaseService[T]):
    """Tenant-scoped, RBAC-checked, audit-logged billing service."""

    def __init__(self, rbac_service: RBACService, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rbac_service = rbac_service

    async def _pre_check(self, permission: str) -> None:
        """RBAC pre-check for the current user and tenant."""
        await self.rbac_service.check_access(
            self.current_user_id, permission, self.current_tenant_id
        )

    async def _execute_with_audit(self, action: str, resource: str, db_op: callable) -> Any:
        """Wrap a DB operation with RBAC check, tenant scoping, and audit logging."""
        await self._pre_check(action)
        status_code = 200
        try:
            result = await db_op()
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            await self._audit(
                action=action,
                resource=resource,
                status=status_code,
                meta={"user_id": self.current_user_id},
            )

    async def list(self, model: Type[T], limit: int = 100, offset: int = 0) -> list[T]:
        """List tenant-scoped billing items."""

        async def db_op():
            stmt = self.scope_query(select(model).limit(limit).offset(offset))
            result = await self.db.execute(stmt)
            return list(result.scalars().all())

        return await self._execute_with_audit("billing:list", model.__name__, db_op)

    async def get_by_id(self, model: Type[T], obj_id: str) -> Optional[T]:
        """Get a single tenant-scoped billing item."""

        async def db_op():
            stmt = self.scope_query(select(model).where(model.id == obj_id))
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        return await self._execute_with_audit("billing:view", model.__name__, db_op)

    async def update(self, obj: T) -> T:
        """Update a billing object with RBAC and audit logging."""

        async def db_op():
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return obj

        # Use transactional block for atomic update
        try:
            await self._pre_check("billing:update")
            async with self.transaction():
                result = await db_op()
                await self._audit(action="billing:update", resource=type(obj).__name__, status=200)
                return result
        except Exception as e:
            await self._audit(
                action="billing:update",
                resource=type(obj).__name__,
                status=500,
                meta={"error": str(e)},
            )
            raise
