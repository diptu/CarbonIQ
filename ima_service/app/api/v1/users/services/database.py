# FILE: ima_service/app/api/v1/users/services/database.py
"""DB-backed user service implementation (async, minimal, reusable)."""

from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.core.log_colors import CLR_ERR, CLR_OK, CLR_RESET, CLR_WARN
from ima_service.app.db.models.user import User

from ..schemas import UserCreate, UserRead, UserUpdate
from .base import UserService
from .helpers import hash_password
from .mappers import to_user_read

_LOG = logging.getLogger(__name__)


class DatabaseUserService(UserService):
    """Concrete user service backed by SQLAlchemy AsyncSession."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------ queries

    async def get_by_id(self, user_id: str) -> Optional[UserRead]:
        row = await self._db.get(User, user_id)
        return to_user_read(row) if row else None

    async def get_by_email(self, email: str) -> Optional[UserRead]:
        stmt = select(User).where(User.email == email).limit(1)
        res = await self._db.execute(stmt)
        row: Optional[User] = res.scalars().first()
        return to_user_read(row) if row else None

    async def list_users(self, limit: int = 50, offset: int = 0) -> Sequence[UserRead]:
        stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        res = await self._db.execute(stmt)
        rows = list(res.scalars().all())
        return [to_user_read(r) for r in rows]

    # ------------------------------ mutations

    async def create(self, payload: UserCreate) -> UserRead:
        if await self._exists_email(payload.email):
            raise ValueError("email already exists")
        if payload.username and await self._exists_username(payload.username):
            raise ValueError("username already exists")

        hpw = hash_password(payload.password)
        user = User(
            email=payload.email,
            username=payload.username,
            hashed_password=hpw,
            role=payload.role,
            first_name=payload.first_name,
            last_name=payload.last_name,
            gender=payload.gender,
        )

        self._db.add(user)
        try:
            await self._db.commit()
            await self._db.refresh(user)
            _LOG.info(
                "%s[user:create]%s id=%s email=%s",
                CLR_OK,
                CLR_RESET,
                user.id,
                user.email,
            )
        except IntegrityError as exc:
            await self._db.rollback()
            _LOG.error(
                "%s[user:create.integrity]%s email/username conflict",
                CLR_ERR,
                CLR_RESET,
            )
            raise ValueError("email or username already exists") from exc

        return to_user_read(user)

    async def update(self, user_id: str, payload: UserUpdate) -> UserRead:
        user = await self._get_or_error(user_id)

        await self._maybe_update_username(user, payload.username)
        self._apply_flags(user, payload)
        self._apply_profile(user, payload)
        if payload.password:
            user.hashed_password = hash_password(payload.password)

        await self._commit_and_refresh(user, action="update")
        return to_user_read(user)

    async def deactivate(self, user_id: str) -> None:
        user = await self._get_or_error(user_id)
        if not user.is_active:
            _LOG.info("%s[user:deactivate.noop]%s id=%s", CLR_OK, CLR_RESET, user_id)
            return
        user.is_active = False
        await self._db.commit()
        _LOG.info("%s[user:deactivate]%s id=%s", CLR_OK, CLR_RESET, user_id)

    # ------------------------------ helpers (private)

    async def _get_or_error(self, user_id: str) -> User:
        user = await self._db.get(User, user_id)
        if not user:
            _LOG.warning("%s[user:missing]%s id=%s", CLR_WARN, CLR_RESET, user_id)
            raise ValueError("user not found")
        return user

    async def _maybe_update_username(
        self, user: User, new_username: Optional[str]
    ) -> None:
        if new_username is None or new_username == user.username:
            return
        if new_username and await self._exists_username(new_username):
            raise ValueError("username already exists")
        user.username = new_username

    @staticmethod
    def _apply_flags(user: User, payload: UserUpdate) -> None:
        if payload.role is not None:
            user.role = payload.role
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.is_superuser is not None:
            user.is_superuser = payload.is_superuser

    @staticmethod
    def _apply_profile(user: User, payload: UserUpdate) -> None:
        if payload.first_name is not None:
            user.first_name = payload.first_name
        if payload.last_name is not None:
            user.last_name = payload.last_name
        if payload.gender is not None:
            user.gender = payload.gender

    async def _commit_and_refresh(self, user: User, *, action: str) -> None:
        try:
            await self._db.commit()
            await self._db.refresh(user)
            _LOG.info("%s[user:%s]%s id=%s", CLR_OK, action, CLR_RESET, user.id)
        except IntegrityError as exc:
            await self._db.rollback()
            _LOG.error(
                "%s[user:%s.integrity]%s id=%s", CLR_ERR, action, CLR_RESET, user.id
            )
            raise ValueError("conflict updating user") from exc

    async def _exists_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email).limit(1)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def _exists_username(self, username: str) -> bool:
        stmt = select(User.id).where(User.username == username).limit(1)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none() is not None
