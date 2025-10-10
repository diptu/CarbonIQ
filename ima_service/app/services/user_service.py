from __future__ import annotations
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.user import User
from app.models.tenant import Tenant


class UserService(BaseService[User]):
    """Async service for managing users, including hierarchical RBAC."""

    def __init__(self, db: AsyncSession, tenant_id: UUID | None = None):
        super().__init__(db=db)
        self.tenant_id = tenant_id

    @log_method_call
    async def create_user(self, user: User) -> User:
        if not user.tenant_id and self.tenant_id:
            user.tenant_id = self.tenant_id

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        log_action(
            "create_user",
            {"user_id": str(user.id), "email": user.email},
            user.tenant_id,
        )
        return user

    @log_method_call
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    @log_method_call
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    @log_method_call
    async def get_by_email_and_tenant(
        self, email: str, tenant_id: UUID | None = None
    ) -> Optional[User]:
        tenant_id = tenant_id or self.tenant_id
        stmt = select(User).where(User.email == email, User.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    @log_method_call
    async def get_users(
        self, skip: int = 0, limit: int = 100, tenant_id: UUID | None = None
    ) -> List[User]:
        tenant_id = tenant_id or self.tenant_id
        stmt = select(User).where(User.tenant_id == tenant_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    @log_method_call
    async def activate_user(self, user: User, cascade: bool = False) -> List[User]:
        users_to_update: List[User] = [user]

        if cascade:
            descendant_tenants = await self._get_descendant_tenants(user.tenant_id)
            stmt = select(User).where(
                User.tenant_id.in_([t.id for t in descendant_tenants])
            )
            result = await self.db.execute(stmt)
            users_to_update.extend(result.scalars().all())

        for u in users_to_update:
            u.is_active = True

        await self.db.commit()
        for u in users_to_update:
            await self.db.refresh(u)
            log_action(
                "activate_user", {"user_id": str(u.id), "email": u.email}, u.tenant_id
            )

        return users_to_update

    @log_method_call
    async def deactivate_user(self, user: User, cascade: bool = False) -> List[User]:
        users_to_update: List[User] = [user]

        if cascade:
            descendant_tenants = await self._get_descendant_tenants(user.tenant_id)
            stmt = select(User).where(
                User.tenant_id.in_([t.id for t in descendant_tenants])
            )
            result = await self.db.execute(stmt)
            users_to_update.extend(result.scalars().all())

        for u in users_to_update:
            u.is_active = False

        await self.db.commit()
        for u in users_to_update:
            await self.db.refresh(u)
            log_action(
                "deactivate_user", {"user_id": str(u.id), "email": u.email}, u.tenant_id
            )

        return users_to_update

    async def _get_descendant_tenants(self, tenant_id: UUID) -> List[Tenant]:
        stmt = select(Tenant).where(Tenant.parent_id == tenant_id)
        result = await self.db.execute(stmt)
        direct_children = result.scalars().all()

        all_descendants = []
        for child in direct_children:
            all_descendants.append(child)
            all_descendants.extend(await self._get_descendant_tenants(child.id))

        return all_descendants
