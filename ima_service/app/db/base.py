"""
File : app/db/base.py
SQLAlchemy base class for declarative models.
"""



from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    # No custom attributes required; extend in model classes as needed.


__all__ = ["Base"]
