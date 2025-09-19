# FILE: ima_service/app/api/v1/users/services/base.py
"""User service interface (abstraction over storage)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from ..schemas import UserCreate, UserRead, UserUpdate


class UserService(ABC):
    """Abstract contract for user operations."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[UserRead]:
        """Return user by ID or None."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserRead]:
        """Return user by email or None."""

    @abstractmethod
    async def list_users(self, limit: int = 50, offset: int = 0) -> Sequence[UserRead]:
        """Return a page of users."""

    @abstractmethod
    async def create(self, payload: UserCreate) -> UserRead:
        """Create and return a user."""

    @abstractmethod
    async def update(self, user_id: str, payload: UserUpdate) -> UserRead:
        """Update and return a user."""

    @abstractmethod
    async def deactivate(self, user_id: str) -> None:
        """Deactivate a user (idempotent)."""
