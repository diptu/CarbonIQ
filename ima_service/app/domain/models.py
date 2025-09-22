"""Domain models (storage-agnostic, compact, prod-ready)."""

from __future__ import annotations
from dataclasses import dataclass
from typing import NewType, Optional
from .schemas import UserRole  # single source of truth for role enum

UserId = NewType("UserId", str)


def normalize_role(v: str | UserRole) -> UserRole:
    """Coerce arbitrary input to a valid UserRole (default: VIEWER)."""
    if isinstance(v, UserRole):
        return v
    try:
        return UserRole(str(v))
    except Exception:
        return UserRole.VIEWER


@dataclass(slots=True, frozen=True)
class UserEntity:
    id: UserId
    role: UserRole
    email: Optional[str] = None
    active: bool = True


__all__ = ["UserId", "UserRole", "normalize_role", "UserEntity"]
