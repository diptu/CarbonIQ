# FILE: ima_service/app/db/base.py
"""
Declarative base for ORM models.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase

__all__ = ["Base"]


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """Base class for all ORM models."""

    # Add shared metadata / mixins if needed.
