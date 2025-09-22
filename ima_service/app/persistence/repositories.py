"""SQLModel-backed user repository helpers (sync, compact, prod-ready)."""

from __future__ import annotations
from datetime import datetime
from typing import Iterable, Optional
from uuid import uuid4
from sqlmodel import Field, Session, SQLModel, select
from .db import get_engine

# ------------------------------- Model ----------------------------------------


class UserSQL(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, index=True)
    email: str | None = Field(default=None, index=True, unique=True)
    role: str = Field(default="viewer", index=True)
    password_hash: str = Field(index=False, nullable=False)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# ------------------------------- CRUD -----------------------------------------


def get_user_by_email(email: str) -> Optional[UserSQL]:
    """Return user by email (or None)."""
    with Session(get_engine()) as s:
        return s.exec(select(UserSQL).where(UserSQL.email == email)).first()


def get_user_by_id(user_id: str) -> Optional[UserSQL]:
    with Session(get_engine()) as s:
        return s.get(UserSQL, user_id)


def list_users() -> list[UserSQL]:
    with Session(get_engine()) as s:
        return list(s.exec(select(UserSQL).order_by(UserSQL.created_at.desc())))


def create_user(*, email: str, role: str, password_hash: str) -> UserSQL:
    u = UserSQL(email=email, role=role.lower(), password_hash=password_hash)
    with Session(get_engine()) as s:
        s.add(u)
        s.commit()
        s.refresh(u)
        return u


def delete_user(user_id: str) -> bool:
    with Session(get_engine()) as s:
        u = s.get(UserSQL, user_id)
        if not u:
            return False
        s.delete(u)
        s.commit()
        return True


def update_user(user_id: str, **fields) -> Optional[UserSQL]:
    allowed = {"email", "role", "password_hash", "is_active"}
    patch = {k: v for k, v in fields.items() if k in allowed}
    if not patch:
        return get_user_by_id(user_id)
    with Session(get_engine()) as s:
        u = s.get(UserSQL, user_id)
        if not u:
            return None
        for k, v in patch.items():
            setattr(u, k, v if k != "role" else str(v).lower())
        s.add(u)
        s.commit()
        s.refresh(u)
        return u


__all__ = [
    "UserSQL",
    "get_user_by_email",
    "get_user_by_id",
    "list_users",
    "create_user",
    "delete_user",
    "update_user",
]
