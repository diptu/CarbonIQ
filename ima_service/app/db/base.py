# FILE: ima_service/app/db/base.py
"""Declarative base and model registry import side-effects."""
# pylint: disable=too-few-public-methods, wrong-import-position
# ruff: noqa: E402  # allow late imports below to avoid circulars

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


# Import models so Alembic/autodiscovery sees them (keep at bottom).
from ima_service.app.db.models.user import User as _User  # noqa: E402,F401
