from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Type
from sqlalchemy import select

from .base_service import BaseService

T = TypeVar("T")


class CRUDService(BaseService[T], Generic[T]):
    """Generic CRUD service with tenant-scoped queries and transaction support."""

    async def list(
        self,
        model: Type[T],
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """List objects with pagination, tenant-scoped."""
        stmt = self.scope_query(select(model)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, model: Type[T], obj_id: str) -> Optional[T]:
        """Get an object by primary key, ensuring tenant scope."""
        obj = await self.db.get(model, obj_id)
        # Check tenant ID explicitly for SQLAlchemy's session.get() which bypasses ORM filters
        if obj and getattr(obj, "tenant_id", None) != self.current_tenant_id:
            return None
        return obj

    async def create(self, obj: T) -> T:
        """Create a new object within a transaction."""
        async with self.transaction():
            self.db.add(obj)
            await self.db.flush()
            # Refresh to ensure object is populated with DB-generated fields (like ID)
            await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        """Update an existing object within a transaction."""
        async with self.transaction():
            await self.db.flush()
            # Refresh to get the latest state from the database after flush/commit
            await self.db.refresh(obj)
        return obj

    async def soft_delete(self, obj: T) -> None:
        """Soft-delete (or hard-delete if no SoftDeleteMixin) an object."""
        async with self.transaction():
            await self.db.delete(obj)
