# ruff: noqa: D100
"""SQLModel user repository (IMA-only)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional
from uuid import UUID, uuid4

from sqlalchemy import true
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, select

from app.core.errors import AppError
from app.domain.models import UserRole
from app.domain.schemas import UserFilter, UserRead


class UserSQL(SQLModel, table=True):
    """users table (owned by IMA)."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=320)
    name: str = Field(max_length=120)
    role: UserRole = Field(sa_column_kwargs={"nullable": False})
    password_hash: str = Field(max_length=128)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = ({"sqlite_autoincrement": True},)


def _map_user(row: UserSQL) -> UserRead:
    """Map SQL row → API model."""
    return UserRead(
        id=row.id,
        email=row.email,
        name=row.name,
        role=row.role,
        is_active=row.is_active,
        created_at=row.created_at,
    )


class SqlUserRepo:
    """Users repo."""

    def __init__(self, session: Session) -> None:
        """Init with a session."""
        self.session = session

    def get(self, user_id: UUID) -> Optional[UserRead]:
        """Fetch user by id."""
        row = self.session.get(UserSQL, user_id)
        return _map_user(row) if row else None

    def get_by_email(self, email: str) -> Optional[UserRead]:
        """Fetch user by email."""
        stmt = select(UserSQL).where(UserSQL.email == email)
        row = self.session.exec(stmt).first()
        return _map_user(row) if row else None

    def list(self, flt: UserFilter) -> Iterable[UserRead]:
        """List users by filters (role/active)."""
        stmt = select(UserSQL)
        if flt.role is not None:
            stmt = stmt.where(UserSQL.role == flt.role)
        if flt.active_only:
            stmt = stmt.where(UserSQL.is_active == true())
        rows = self.session.exec(stmt).all()
        return [_map_user(r) for r in rows]

    def create(  # pylint: disable=too-many-arguments
        self,
        *,
        email: str,
        name: str,
        role: UserRole,
        password_hash: str,
        is_active: bool = True,
    ) -> UserRead:
        """Insert user; unique email -> AppError(409)."""
        row = UserSQL(
            email=email,
            name=name,
            role=role,
            password_hash=password_hash,
            is_active=is_active,
        )
        self.session.add(row)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                status_code=409,
                code="USER_EMAIL_EXISTS",
                message="Email already in use.",
                details={"email": email},
            ) from exc
        self.session.refresh(row)
        return _map_user(row)
