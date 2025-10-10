"""Register all SQLAlchemy models for Alembic autogeneration.

This module ensures Alembic can detect all models when running
`alembic revision --autogenerate`.
"""

from .base_class import Base

# Import all models here to enable Alembic autogeneration
# Example:
from ima_service.app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission

__all__ = ["Base"]
