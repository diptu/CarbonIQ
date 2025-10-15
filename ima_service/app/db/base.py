"""Register all SQLAlchemy models for Alembic autogeneration.

Notes:
- Import this module in `migrations/env.py` to enable Alembic detection.
- All new models should be imported here.
"""

# pylint: disable=unused-import
from app.models.audit_log import AuditLog
from app.models.auth_tokens import AuthToken
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole

from .base_class import Base

__all__ = ["Base"]
