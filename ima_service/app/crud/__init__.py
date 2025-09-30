"""CRUD package: exposes user, role, and user_roles operations."""

from .role import create_role, delete_role, get_role_by_name, get_roles, update_role
from .user_basic import (
    create_user,
    deactivate_user,
    delete_user,
    get_user,
    get_user_by_email,
    list_users,
    reactivate_user,
)
from .user_queries import get_user_by_email as get_user_by_email_with_roles
from .user_queries import get_users as get_users_with_roles
from .user_roles import assign_role_to_user
