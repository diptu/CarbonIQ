# ruff: noqa: D100
"""Domain entities (users only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class UserRole(str, Enum):
    """String-valued user roles for auth/claims."""

    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


def _now() -> datetime:
    """UTC timestamp helper."""
    return datetime.now(timezone.utc)


@dataclass
class User:
    """User aggregate persisted by IMA."""

    email: str
    name: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_now)
