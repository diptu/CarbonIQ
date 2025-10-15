from __future__ import annotations
from typing import Any, Type, Optional
from sqlalchemy import select

from .base_service import BaseService
from .rbac_service import RBACService

T = Any  # Generic ORM model placeholder


class ReportingService(BaseService[T]):
    """Tenant-scoped, RBAC-checked, audit-logged reporting service."""

    def __init__(self, rbac_service: RBACService, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rbac_service = rbac_service

    async def _pre_check(self, permission: str) -> None:
        await self.rbac_service.check_access(
            self.current_user_id, permission, self.current_tenant_id
        )

    async def _execute(self, action: str, resource: str, db_op: callable) -> Any:
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

    async def list(self, model: Type[T], limit: int = 100, offset: int = 0) -> list[T]:
        return await self._execute(
            "report:list",
            model.__name__,
            lambda: self.db.execute(
                self.scope_query(select(model).limit(limit).offset(offset))
            ).then(lambda r: list(r.scalars().all())),
        )

    async def get_by_id(self, model: Type[T], obj_id: str) -> Optional[T]:
        return await self._execute(
            "report:view",
            model.__name__,
            lambda: self.db.execute(self.scope_query(select(model).where(model.id == obj_id))).then(
                lambda r: r.scalar_one_or_none()
            ),
        )

    async def update(self, obj: T) -> T:
        async def op():
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return obj

        try:
            await self._pre_check("report:update")
            async with self.transaction():
                result = await op()
                await self._audit("report:update", type(obj).__name__, 200)
                return result
        except Exception as e:
            await self._audit("report:update", type(obj).__name__, 500, meta={"error": str(e)})
            raise
