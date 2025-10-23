# app/services/user_service.py
from __future__ import annotations
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..models.user import User
from ..models.role import Role
from ..models.auth_tokens import AuthToken, InvitationToken
from .base_service import BaseService
from .rbac_service import RBACService


class UserService(BaseService[User]):
    """
    Tenant-scoped user service with RBAC, lifecycle management,
    and audit-ready operations.
    """

    def __init__(self, rbac_service: RBACService, **kwargs):
        super().__init__(**kwargs)
        self.rbac_service = rbac_service

    # --------------------------- READ METHODS ---------------------------

    async def get_by_email(self, email: str, ignore_tenant: bool = False) -> Optional[User]:
        """
        Retrieve a user by email. Optionally ignore tenant scope.
        """
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.auth_tokens),
            )
            .where(User.email == email)
        )
        if not ignore_tenant:
            stmt = self.scope_query(stmt)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID within tenant scope.
        """
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.auth_tokens),
            )
            .where(User.id == user_id)
        )
        stmt = self.scope_query(stmt)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        List users with pagination, tenant-scoped and RBAC-checked.
        """
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

    # --------------------------- WRITE METHODS ---------------------------

    @BaseService.transactional
    async def create_user(self, user: User) -> User:
        """
        Create a user after RBAC check and tenant enforcement.
        """
        await self.rbac_service.check_access(
            self.current_user_id, "user:create", self.current_tenant_id
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    @BaseService.transactional
    async def update_user(self, user: User) -> User:
        """
        Update a user after RBAC check and tenant enforcement.
        """
        await self.rbac_service.check_access(
            self.current_user_id, "user:update", self.current_tenant_id
        )
        if getattr(user, "tenant_id", None) != self.current_tenant_id:
            raise PermissionError("Cannot update user outside tenant scope.")
        await self.db.flush()
        await self.db.refresh(user)
        return user

    @BaseService.transactional
    async def deactivate_user(self, user: User) -> None:
        """
        Deactivate a user and revoke their auth tokens.
        """
        await self.rbac_service.check_access(
            self.current_user_id, "user:deactivate", self.current_tenant_id
        )
        if getattr(user, "tenant_id", None) != self.current_tenant_id:
            raise PermissionError("Cannot deactivate user outside tenant scope.")

        user.is_active = False
        stmt = update(AuthToken).where(AuthToken.user_id == user.id).values(revoked=True)
        await self.db.execute(stmt)

    @BaseService.transactional
    async def invite_user(self, email: str, roles: Optional[List[str]] = None) -> InvitationToken:
        """
        Create an invitation token for a new user, enforcing RBAC and tenant scope.
        """
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

    # --------------------------- PERMISSIONS HELPERS ---------------------------

    async def get_user_permissions(self, user: User) -> List[str]:
        """
        Return a list of permission codes for a user via their roles.
        """
        perms = {
            perm.code
            for role in getattr(user, "roles", [])
            for perm in getattr(role, "permissions", [])
        }
        return list(perms)
