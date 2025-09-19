# FILE: ima_service/app/api/v1/users/utils.py
"""Utilities for role hierarchy, permissions, and error helpers."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from ima_service.app.domain.users.enums import UserRole


class _Rank(IntEnum):
    USER = 0
    MODERATOR = 1
    ADMIN = 2


_ROLE_TO_RANK: Final[dict[UserRole, _Rank]] = {
    UserRole.USER: _Rank.USER,
    UserRole.MODERATOR: _Rank.MODERATOR,
    UserRole.ADMIN: _Rank.ADMIN,
}


def role_gte(a: UserRole, b: UserRole) -> bool:
    """Return True if role `a` has at least the privileges of role `b`."""
    return _ROLE_TO_RANK[a] >= _ROLE_TO_RANK[b]


def require_min_role(user_role: UserRole, min_role: UserRole) -> None:
    """Raise PermissionError if `user_role` is below `min_role`."""
    if not role_gte(user_role, min_role):
        raise PermissionError(f"Insufficient role: have={user_role}, need>={min_role}")
