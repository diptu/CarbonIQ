"""CRUD package: exposes user, role, and user_roles operations."""

from .user_basic import (
    get_user_by_email,
    get_user,
    create_user,
    list_users,
    deactivate_user,
    reactivate_user,
    delete_user,
)
from .user_queries import (
    get_user_by_email as get_user_by_email_with_roles,
    get_users as get_users_with_roles,
)
from .role import get_role_by_name, get_roles, create_role, update_role, delete_role
from .user_roles import assign_role_to_user
