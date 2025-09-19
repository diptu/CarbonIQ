# FILE: ima_service/app/api/v1/users/services/mappers.py
"""Mappers between ORM models and API schemas (shared enums mean no conversion)."""

from __future__ import annotations

from ima_service.app.db.models.user import User

from ..schemas import UserRead


def to_user_read(u: User) -> UserRead:
    """Map ORM User -> API UserRead."""
    return UserRead(
        id=u.id,
        email=u.email,
        username=u.username,
        first_name=u.first_name,
        last_name=u.last_name,
        gender=u.gender,  # same enum type
        role=u.role,  # same enum type
        is_active=u.is_active,
        is_superuser=u.is_superuser,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )
