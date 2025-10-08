import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, text, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi import HTTPException
from ..db.base_class import Base, TimestampMixin
from .user_roles import UserRole
from .role import Role
from .permission import Permission
from sqlalchemy import text


class User(Base, TimestampMixin):
    """
    Represents a system user.
    Each user belongs to a specific tenant (company/sub-company).
    Supports role-based access via UserRole association table.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 🔗 Tenant Ownership
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # 🧩 Created By (self-reference)
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by = relationship(
        "User",
        remote_side=[id],
        backref=backref("created_users", lazy="selectin"),
        lazy="selectin",
    )

    # 🧠 Role-Based Access Control (many-to-many)
    roles_association = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    roles = relationship(
        "Role",
        secondary="user_roles",
        viewonly=True,
        back_populates="users",
        lazy="selectin",
    )

    # ---------------------------
    # 🔹 Utility Methods
    # ---------------------------
    def __repr__(self) -> str:
        return f"<User(email={self.email}, tenant_id={self.tenant_id}, active={self.is_active})>"

    def has_role(self, role_name: str) -> bool:
        """Check if the user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    # ---------------------------
    # 🔹 Multi-Tenant Access Control
    # ---------------------------
    async def have_access(self, target_tenant_id: str, db: AsyncSession) -> bool:
        """
        Returns True if the user has access to the target tenant.
        Access is granted if:
        - The target tenant is the user's own tenant
        - OR the target tenant is a child of the user's tenant (via tenants.parent_id)
        """
        # Same tenant → allow
        if str(self.tenant_id) == target_tenant_id:
            return True

        # Check if target tenant is a child of user's tenant
        sql = text("""
            SELECT 1
            FROM tenants
            WHERE id = :target_tenant_id
              AND parent_id = :user_tenant_id
            LIMIT 1
        """)
        result = await db.execute(
            sql,
            {
                "target_tenant_id": target_tenant_id,
                "user_tenant_id": str(self.tenant_id),
            },
        )

        return bool(result.scalar_one_or_none())

    async def enforce_access(self, target_tenant_id: str, db: AsyncSession):
        """Raise 403 if user cannot access target tenant."""
        if not await self.have_access(target_tenant_id, db):
            raise HTTPException(
                status_code=403, detail=f"Access denied to tenant {target_tenant_id}"
            )

    async def can_perform_action(self, permission_name: str) -> bool:
        """Returns True if the user has a role granting the given permission."""
        for role in self.roles:
            if permission_name in [p.name for p in role.permissions]:
                return True
        return False
