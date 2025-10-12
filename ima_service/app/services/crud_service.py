"""Generic CRUD service."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar
from sqlalchemy import select


from .base_service import BaseService

T = TypeVar("T")


class CRUDService(BaseService[T], Generic[T]):
    """Generic CRUD operations for any SQLAlchemy model."""

    async def list(
        self,
        model: type[T],
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """
        List objects of the given model with pagination.

        Parameters
        ----------
        model : type[T]
            SQLAlchemy model class.
        limit : int
            Max number of records to return.
        offset : int
            Number of records to skip.

        Returns
        -------
        List[T]
            List of model instances.
        """
        stmt = select(model).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())  # ensure list[T] type

    async def get_by_id(self, model: type[T], obj_id: str) -> Optional[T]:
        """
        Get a single object by primary key.

        Parameters
        ----------
        model : type[T]
            SQLAlchemy model class.
        obj_id : str
            Primary key value.

        Returns
        -------
        Optional[T]
            The object if found, else None.
        """
        return await self.db.get(model, obj_id)

    async def create(self, obj: T) -> T:
        """
        Add a new object to the database.

        Parameters
        ----------
        obj : T
            The object instance to create.

        Returns
        -------
        T
            The created object with updated state.
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        """
        Commit changes to an existing object.

        Parameters
        ----------
        obj : T
            The object instance to update.

        Returns
        -------
        T
            The updated object with refreshed state.
        """
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def soft_delete(self, obj: T) -> None:
        """
        Delete an object from the database.

        Parameters
        ----------
        obj : T
            The object instance to delete.
        """
        await self.db.delete(obj)
        await self.db.commit()
