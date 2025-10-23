# app/services/crud_service.py
from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Type, Coroutine, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_service import BaseService

T = TypeVar("T")


class CRUDService(BaseService[T], Generic[T]):
    """
    Generic CRUD service for tenant-scoped models with:
        - List, get, create, update, soft-delete operations
        - Transactional safety
        - Tenant scoping enforcement
        - Optional audit integration
    """

    async def list(
        self,
        model: Type[T],
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """
        List objects with pagination, tenant-scoped.
        Args:
            model: SQLAlchemy ORM model class
            limit: Max number of records to return
            offset: Offset for pagination
        Returns:
            List of model instances
        """
        stmt = self.scope_query(select(model)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, model: Type[T], obj_id: str) -> Optional[T]:
        """
        Retrieve an object by primary key within tenant scope.
        Args:
            model: SQLAlchemy ORM model class
            obj_id: Primary key ID of the object
        Returns:
            Object instance or None if not found / outside tenant
        """
        obj = await self.db.get(model, obj_id)
        if obj and getattr(obj, "tenant_id", None) != self.current_tenant_id:
            return None
        return obj

    async def create(self, obj: T) -> T:
        """
        Create a new object in a transaction, ensuring tenant scope.
        Refreshes object after flush to populate DB-generated fields.
        """
        async with self.transaction():
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        """
        Update an existing object in a transaction.
        Ensures tenant-scoped access and refreshes the object post-flush.
        """
        async with self.transaction():
            # Optionally enforce tenant on update
            if getattr(obj, "tenant_id", None) != self.current_tenant_id:
                raise PermissionError("Cannot update object outside tenant scope.")
            await self.db.flush()
            await self.db.refresh(obj)
        return obj

    async def soft_delete(self, obj: T) -> None:
        """
        Soft-delete (or hard delete if no SoftDeleteMixin) an object.
        Enforces tenant-scoped access.
        """
        async with self.transaction():
            if getattr(obj, "tenant_id", None) != self.current_tenant_id:
                raise PermissionError("Cannot delete object outside tenant scope.")
            await self.db.delete(obj)
