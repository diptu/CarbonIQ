# app/models/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from .user_roles import UserRole
from .role_permissions import RolePermission
from .role import Role
from .tenant import Tenant
from sqlalchemy.orm import Mapped, relationship


class User(Base, TimestampMixin):
    # existing fields ...
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    tenant: Mapped[Tenant] = relationship(
        "Tenant", back_populates="users", lazy="selectin"
    )

    # ---------------------------
    # 🔹 RBAC Helpers
    # ---------------------------
    def has_role(self, role_name: str) -> bool:
        """Check if the user has a specific role assigned."""
        return any(role.name == role_name for role in self.roles)

    async def can_perform_action(self, permission_name: str, db: AsyncSession) -> bool:
        """
        Check if user has a role granting the given permission using ORM queries.
        Efficient for large role/permission sets.
        """
        stmt = (
            select(RolePermission)
            .join(Role, RolePermission.role_id == Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == self.id)
            .where(
                RolePermission.permission_id.in_(
                    select(RolePermission.permission_id)
                    .join(Permission)
                    .where(Permission.name == permission_name)
                )
            )
        )
        result = await db.execute(stmt)
        return bool(result.scalar_one_or_none())

    # ---------------------------
    # 🔹 Multi-Tenant Access Control
    # ---------------------------
    async def have_access(self, target_tenant_id: str, db: AsyncSession) -> bool:
        """Returns True if user can access target tenant (own or child)."""
        # Own tenant → allow
        if str(self.tenant_id) == target_tenant_id:
            return True

        # Check child tenant using ORM
        stmt = select(Tenant.id).where(
            Tenant.id == target_tenant_id, Tenant.parent_id == self.tenant_id
        )
        result = await db.execute(stmt)
        return bool(result.scalar_one_or_none())

    async def enforce_access(self, target_tenant_id: str, db: AsyncSession):
        """Raise 403 if user cannot access target tenant."""
        if not await self.have_access(target_tenant_id, db):
            raise HTTPException(
                status_code=403, detail=f"Access denied to tenant {target_tenant_id}"
            )
