"""Register all SQLAlchemy models for Alembic autogeneration."""

from .base_class import Base

# All models must be imported in `migrations/env.py` to enable Alembic detection
__all__ = ["Base"]
