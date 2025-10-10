# app/db/base.py
"""
Import all ORM models so Alembic autogenerate sees them.

Place this file where the app package is importable by Alembic.
Alembic's env.py should import app.db.base so SQLA metadata
is registered before autogeneration runs.
"""

from __future__ import annotations

# ensure Base is available for Alembic to reference
from .base_class import Base  # noqa: F401

# Import all models here. Keep imports explicit so static checks
# and Alembic autogeneration can find model definitions.
#
# Adjust these imports if your models live in a different module path.
from app.models.tenant import Tenant  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.user_roles import UserRole  # noqa: F401
from app.models.role_permission import RolePermission  # noqa: F401

__all__ = ["Base"]
