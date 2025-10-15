from __future__ import annotations
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, joinedload

from ..models.user import User
from ..models.role import Role
from ..models.auth_tokens import AuthToken, InvitationToken
from .base_service import BaseService
from .rbac_service import RBACService


class UserService(BaseService[User]):
    """Tenant-scoped user service with RBAC and lifecycle management."""

    def __init__(self, rbac_service: RBACService, **kwargs):
        super().__init__(**kwargs)
        self.rbac_service = rbac_service

    # --- Read Methods ---
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),  # class-bound attribute
                selectinload(User.auth_tokens),
            )
            .where(User.email == email)
        )
        stmt = self.scope_query(stmt)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),  # class-bound attribute
                selectinload(User.auth_tokens),
            )
            .where(User.id == user_id)
        )
        stmt = self.scope_query(stmt)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        await self.rbac_service.check_access(
            self.current_user_id, "user:list", self.current_tenant_id
        )
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.auth_tokens),
            )
            .limit(limit)
            .offset(offset)
        )
        stmt = self.scope_query(stmt)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # --- Write Methods ---
    @BaseService.transactional
    async def create_user(self, user: User) -> User:
        await self.rbac_service.check_access(
            self.current_user_id, "user:create", self.current_tenant_id
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    @BaseService.transactional
    async def update_user(self, user: User) -> User:
        await self.rbac_service.check_access(
            self.current_user_id, "user:update", self.current_tenant_id
        )
        await self.db.flush()
        await self.db.refresh(user)
        return user

    @BaseService.transactional
    async def deactivate_user(self, user: User) -> None:
        await self.rbac_service.check_access(
            self.current_user_id, "user:deactivate", self.current_tenant_id
        )
        user.is_active = False
        stmt = update(AuthToken).where(AuthToken.user_id == user.id).values(revoked=True)
        await self.db.execute(stmt)

    @BaseService.transactional
    async def invite_user(self, email: str, roles: Optional[List[str]] = None) -> InvitationToken:
        await self.rbac_service.check_access(
            self.current_user_id, "user:invite", self.current_tenant_id
        )
        invite = InvitationToken(
            email=email,
            tenant_id=self.current_tenant_id,
            status="PENDING",
            invited_by_id=self.current_user_id,
        )
        self.db.add(invite)
        await self.db.flush()
        await self.db.refresh(invite)
        return invite
