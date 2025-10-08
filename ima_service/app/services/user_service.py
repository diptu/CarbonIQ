# app/services/user_service.py
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import aliased

from app.models.user import User
from app.models.role import Role
from app.models.user_roles import UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.base_service import BaseService
from ima_service.app.models.tenants import Tenant


class UserService(BaseService):
    """User-related business logic."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_accessible_tenants(self, user_tenant_id: UUID) -> List[UUID]:
        """Return tenant + all child tenants using ORM recursive CTE."""
        tenant_cte = (
            select(Tenant.id, Tenant.parent_id)
            .where(Tenant.id == user_tenant_id)
            .cte(name="tenant_cte", recursive=True)
        )

        tenant_alias = aliased(Tenant, name="t")
        tenant_cte = tenant_cte.union_all(
            select(tenant_alias.id, tenant_alias.parent_id).where(
                tenant_alias.parent_id == tenant_cte.c.id
            )
        )

        result = await self.db.execute(select(tenant_cte.c.id))
        tenant_ids = [row[0] for row in result.fetchall()]
        return tenant_ids

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        tenant_id: UUID = None,
        include_inactive: bool = False,
    ) -> Tuple[int, List[User]]:
        """Return users under tenant + all child tenants."""
        if tenant_id:
            tenant_ids = await self.get_accessible_tenants(tenant_id)
        else:
            tenant_ids = []

        stmt = select(User).where(User.tenant_id.in_(tenant_ids))
        if not include_inactive:
            stmt = stmt.where(User.is_active == True)

        total_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = total_result.scalar() or 0

        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return total, users

    async def get_role_by_name(self, name: str, tenant_id: UUID) -> Role:
        stmt = select(Role).where(Role.name == name, Role.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError(f"Role {name} not found in tenant {tenant_id}")
        return role

    @BaseService.log_action("user.create")
    async def create_user(self, email: str, password: str, tenant_id: UUID) -> User:
        hashed_password = hash_password(password)
        new_user = User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            tenant_id=tenant_id,
            is_superuser=False,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Assign default VIEWER role
        viewer_role = await self.get_role_by_name("VIEWER", tenant_id)
        if viewer_role:
            self.db.add(
                UserRole(
                    user_id=new_user.id, role_id=viewer_role.id, tenant_id=tenant_id
                )
            )
            await self.db.commit()

        return new_user

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        tenant_id: Optional[UUID] = None,
        include_inactive: bool = False,
    ) -> Tuple[int, List[User]]:
        tenant_ids = await self.get_accessible_tenants(tenant_id) if tenant_id else []

        stmt = select(User).where(User.tenant_id.in_(tenant_ids))
        if not include_inactive:
            stmt = stmt.where(User.is_active == True)
        total_result = await self.db.execute(stmt)
        total = total_result.scalars().unique().count()

        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return total, users

    async def get_user_by_email(
        self, email: str, tenant_id: Optional[UUID] = None
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        if tenant_id:
            stmt = stmt.where(User.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        if not getattr(user, "is_active", True):
            raise HTTPException(status_code=403, detail="Account is inactive.")
        return user

    def create_tokens_for_user(self, user: User, roles: List[str]) -> dict:
        access_token = create_access_token(
            user_id=user.id, tenant_id=user.tenant_id, roles=roles
        )
        refresh_token = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)
        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "Bearer",
            "expiresIn": 3600,
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": roles,
        }
