"""Register all SQLAlchemy models for Alembic autogeneration.

Notes
-----
- Import this module in `migrations/env.py` to enable Alembic detection.
- All new models should be imported here or in `migrations/env.py`.
- noqa comments suppress unused-import warnings.
"""

# Import all your ORM models here so Alembic can see them
# pylint: disable=unused-import
from app.models.audit_log import AuditLog  # type: ignore
from app.models.auth_tokens import AuthToken  # type: ignore
from app.models.permission import Permission  # type: ignore
from app.models.role import Role  # type: ignore
from app.models.user import User  # type: ignore

from .base_class import Base

__all__ = ["Base"]
