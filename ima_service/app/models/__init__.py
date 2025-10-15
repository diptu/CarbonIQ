# app/models/__init__.py

"""
Aggregate all SQLAlchemy models for easy import.

This allows Alembic to detect metadata for autogenerate migrations.
"""

# Import all models here
from ..models.user import User
from ..models.role import Role
from ..models.permission import Permission
from ..models.role_permission import RolePermission
from ..models.user_role import UserRole
from ..models.auth_tokens import AuthToken, InvitationToken
from ..models.audit_log import AuditLog


# Add more imports as you create new models

# Expose Base metadata
from ..db.base_class import Base

__all__ = [
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Base",
]
