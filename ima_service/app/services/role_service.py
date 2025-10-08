# app/services/role_service.py
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_roles import UserRole
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """Service to manage Roles and Permissions for tenants."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------
    # Role CRUD
    # -------------------------------
    async def create_role(self, tenant_id: UUID, role_in: RoleCreate) -> Role:
        role = Role(
            id=uuid4(),
            tenant_id=tenant_id,
            name=role_in.name,
            description=role_in.description,
        )
        self.db.add(role)
        try:
            await self.db.commit()
            await self.db.refresh(role)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(
                f"Role '{role_in.name}' already exists in tenant {tenant_id}"
            )
        return role

    async def get_role(
        self, role_id: UUID, tenant_id: Optional[UUID] = None
    ) -> Optional[Role]:
        stmt = select(Role).where(Role.id == role_id)
        if tenant_id:
            stmt = stmt.where(Role.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_roles_for_tenant(self, tenant_id: UUID) -> List[Role]:
        stmt = select(Role).where(Role.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_role(self, role_id: UUID, role_in: RoleUpdate) -> Role:
        role = await self.get_role(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        for field, value in role_in.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: UUID) -> None:
        role = await self.get_role(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        await self.db.delete(role)
        await self.db.commit()

    # -------------------------------
    # Role Permissions
    # -------------------------------
    async def assign_permission(self, role_id: UUID, permission_id: UUID) -> None:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(rp)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            # permission already assigned
            pass

    async def get_permissions_for_role(self, role_id: UUID) -> List[Permission]:
        stmt = (
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == role_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def remove_permission(self, role_id: UUID, permission_id: UUID) -> None:
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        result = await self.db.execute(stmt)
        rp = result.scalar_one_or_none()
        if rp:
            await self.db.delete(rp)
            await self.db.commit()

    # -------------------------------
    # User Role Assignment
    # -------------------------------
    async def assign_role_to_user(
        self, user_id: UUID, role_id: UUID, tenant_id: UUID
    ) -> None:
        ur = UserRole(user_id=user_id, role_id=role_id, tenant_id=tenant_id)
        self.db.add(ur)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            # role already assigned
            pass

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> None:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        ur = result.scalar_one_or_none()
        if ur:
            await self.db.delete(ur)
            await self.db.commit()
