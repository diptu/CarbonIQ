# app/services/user_service.py

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession, tenant_id):
        self.db = db
        self.tenant_id = tenant_id

    async def get_by_id(self, user_id):
        """
        Get a single user by ID within the tenant scope.
        """
        query = select(User).where(User.id == user_id)
        if self.tenant_id:
            query = query.where(User.tenant_id == self.tenant_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_users(
        self, skip: int = 0, limit: int = 100, return_count: bool = False
    ):
        """
        Get users for the current tenant with optional pagination count.
        """
        query = (
            select(User)
            .where(User.tenant_id == self.tenant_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        users = result.scalars().all()

        if return_count:
            count_query = (
                select(func.count())
                .select_from(User)
                .where(User.tenant_id == self.tenant_id)
            )
            total_result = await self.db.execute(count_query)
            total_count = total_result.scalar_one()
            return users, total_count

        return users
