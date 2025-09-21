# ruff: noqa: D100
# pylint: disable=missing-class-docstring,missing-function-docstring,
# pylint: disable=too-few-public-methods,too-many-arguments
"""Domain services: users & auth (no org/membership)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, Optional, Protocol
from uuid import UUID

from app.core.errors import AppError
from app.core.security import create_access_token, create_refresh_token
from app.core.settings import get_settings
from app.domain.schemas import TokenPair, UserCreate, UserFilter, UserRead, UserRole


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, password_hash: str) -> bool: ...


class UserRepo(Protocol):
    def get(self, user_id: UUID) -> Optional[UserRead]: ...
    def get_by_email(self, email: str) -> Optional[UserRead]: ...
    def list(self, flt: UserFilter) -> Iterable[UserRead]: ...
    def create(
        self,
        *,
        email: str,
        name: str,
        role: UserRole,
        password_hash: str,
        is_active: bool = True,
    ) -> UserRead: ...


@dataclass
class UserService:
    users: UserRepo
    hasher: PasswordHasher

    def get_user(self, user_id: UUID) -> UserRead:
        user = self.users.get(user_id)  # pylint: disable=assignment-from-no-return
        if not user:
            raise AppError(
                status_code=404, code="USER_NOT_FOUND", message="User not found."
            )
        return user

    def list_users(self, flt: UserFilter) -> list[UserRead]:
        return list(self.users.list(flt))  # pylint: disable=assignment-from-no-return

    def create_user(self, data: UserCreate) -> UserRead:
        if self.users.get_by_email(  # pylint: disable=assignment-from-no-return
            data.email
        ):
            raise AppError(
                status_code=409,
                code="USER_EMAIL_EXISTS",
                message="Email already in use.",
                details={"email": data.email},
            )
        pwd_hash = self.hasher.hash(  # pylint: disable=assignment-from-no-return
            data.password
        )
        return self.users.create(  # pylint: disable=assignment-from-no-return
            email=data.email,
            name=data.name,
            role=data.role,
            password_hash=pwd_hash,
            is_active=True,
        )

    def issue_tokens(self, user_id: UUID) -> TokenPair:
        user = self.get_user(user_id)
        st = get_settings()
        claims = {"sub": str(user.id), "email": user.email, "role": user.role}
        access = create_access_token(
            claims, expires=timedelta(minutes=st.jwt.access_expire_minutes)
        )
        refresh = create_refresh_token(
            {"sub": str(user.id)}, expires=timedelta(days=st.jwt.refresh_expire_days)
        )
        return TokenPair(access=access, refresh=refresh)
