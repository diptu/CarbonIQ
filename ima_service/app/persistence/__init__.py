"""Persistence layer exports (engine/session + user repo)."""

from .db import get_engine, get_session, init_db
from .repositories import (
    UserSQL,
    get_user_by_email,
    get_user_by_id,
    list_users,
    create_user,
    delete_user,
    update_user,
)

__all__ = [
    "get_engine",
    "get_session",
    "init_db",
    "UserSQL",
    "get_user_by_email",
    "get_user_by_id",
    "list_users",
    "create_user",
    "delete_user",
    "update_user",
]
