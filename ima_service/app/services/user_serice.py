"""User service"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .base_service import BaseService


class UserService(BaseService[User]):
    """User service with optional RLS."""

    def __init__(self, db: AsyncSession, tenant_id: str, actor_id: str):
        super().__init__(db=db, tenant_id=tenant_id, actor_id=actor_id)
        self.rls_enabled: bool = True

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
