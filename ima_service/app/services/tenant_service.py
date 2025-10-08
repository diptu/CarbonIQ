# app/services/tenant_service.py
from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.tenants import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate
from app.services.base_service import BaseService


class TenantService(BaseService):
    """Service to manage Tenants and sub-tenants with schema isolation."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    @BaseService.log_action("tenant.create")
    async def create_tenant(
        self, tenant_in: TenantCreate, parent_id: Optional[UUID] = None
    ) -> Tenant:
        tenant = Tenant(
            name=tenant_in.name,
            domain=tenant_in.domain,
            schema_name=tenant_in.schema_name,
            parent_id=parent_id,
        )
        self.db.add(tenant)
        try:
            await self.db.commit()
            await self.db.refresh(tenant)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Tenant with same domain/schema exists")
        return tenant

    async def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tenants(self) -> List[Tenant]:
        stmt = select(Tenant)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_sub_tenants(self, parent_id: UUID) -> List[Tenant]:
        stmt = select(Tenant).where(Tenant.parent_id == parent_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all_child_tenants(self, parent_id: UUID) -> List[Tenant]:
        """Recursively fetch all child tenants using ORM."""
        children = []

        async def recurse(pid: UUID):
            subs = await self.get_sub_tenants(pid)
            for sub in subs:
                children.append(sub)
                await recurse(sub.id)

        await recurse(parent_id)
        return children

    @BaseService.log_action("tenant.update")
    async def update_tenant(self, tenant_id: UUID, tenant_in: TenantUpdate) -> Tenant:
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")
        for field, value in tenant_in.model_dump(exclude_unset=True).items():
            setattr(tenant, field, value)
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant

    @BaseService.log_action("tenant.delete")
    async def delete_tenant(self, tenant_id: UUID) -> None:
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")
        await self.db.delete(tenant)
        await self.db.commit()
