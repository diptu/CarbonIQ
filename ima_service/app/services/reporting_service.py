# app/services/reporting_service.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService


class ReportingService(BaseService):
    """
    Reporting service that uses existing IMA models (Tenant/User/Role/
    Permission). Defensive: if optional models are missing, the methods
    degrade gracefully.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def tenant_summary(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Return a small summary for a tenant using available models:
        - total_users
        - total_roles
        - total_permissions
        If a model is not present in the project, it will return None
        for that metric rather than raising an ImportError.
        """
        out: Dict[str, Optional[int]] = {
            "tenant_id": str(tenant_id),
            "total_users": None,
            "total_roles": None,
            "total_permissions": None,
        }

        # Users
        try:
            from app.models.user import User  # type: ignore

            stmt = (
                select(func.count())
                .select_from(User)
                .where(User.tenant_id == tenant_id)
            )
            res = await self.db.execute(stmt)
            out["total_users"] = int(res.scalar() or 0)
        except Exception:
            # If user model is not present / other DB error, leave None
            out["total_users"] = None

        # Roles
        try:
            from app.models.role import Role  # type: ignore

            stmt = (
                select(func.count())
                .select_from(Role)
                .where(Role.tenant_id == tenant_id)
            )
            res = await self.db.execute(stmt)
            out["total_roles"] = int(res.scalar() or 0)
        except Exception:
            out["total_roles"] = None

        # Permissions
        try:
            from app.models.permission import Permission  # type: ignore

            stmt = (
                select(func.count())
                .select_from(Permission)
                .where(Permission.tenant_id == tenant_id)
            )
            res = await self.db.execute(stmt)
            out["total_permissions"] = int(res.scalar() or 0)
        except Exception:
            out["total_permissions"] = None

        return out

    async def tenants_overview(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Return a list of tenant summaries. If Tenant model exists, iterate
        tenants and reuse tenant_summary for each.
        """
        from app.models.tenants import Tenant  # type: ignore

        stmt = (
            select(Tenant).order_by(Tenant.created_at.desc()).offset(skip).limit(limit)
        )
        res = await self.db.execute(stmt)
        tenants = res.scalars().all()
        tasks: List[Dict] = []
        for t in tenants:
            tasks.append(await self.tenant_summary(t.id))
        return tasks

    async def count_users_by_role(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        Return counts of users grouped by role for a tenant. If Role or
        UserRole models missing, returns empty list.
        """
        try:
            from app.models.user_roles import UserRole  # type: ignore
            from app.models.role import Role  # type: ignore
            from app.models.user import User  # type: ignore

            stmt = (
                select(Role.name, func.count(UserRole.user_id).label("cnt"))
                .join(UserRole, Role.id == UserRole.role_id)
                .where(Role.tenant_id == tenant_id)
                .group_by(Role.name)
            )
            res = await self.db.execute(stmt)
            return [{"role": row[0], "count": int(row[1])} for row in res.fetchall()]
        except Exception:
            return []
