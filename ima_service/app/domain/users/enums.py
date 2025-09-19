# FILE: ima_service/app/domain/users/enums.py
"""Reusable user enums shared across ORM, schemas, and services."""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Hierarchical user roles (ascending privileges)."""

    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserGender(str, Enum):
    """User gender options (string-backed for portability)."""

    UNSPECIFIED = "UNSPECIFIED"
    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"
    OTHER = "OTHER"
