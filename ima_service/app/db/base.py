"""Register all SQLAlchemy models so Alembic can detect them for migrations."""

# Import all models to register them with SQLAlchemy metadata
# pylint: disable=unused-import
from .base_class import Base

__all__ = ["Base"]
