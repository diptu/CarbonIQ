"""
File: app/api/v1/docs/role.py
OpenAPI documentation for User endpoints.
"""

from fastapi import status

# ============================================================
# Create Role
# ============================================================
CREATE_ROLE_DOCS = {
    "summary": "Create a new role",
    "description": (
        "Creates a new role. Role names must be unique. "
        "If a role with the same name already exists, a conflict error is returned."
    ),
    "responses": {
        status.HTTP_201_CREATED: {"description": "Role created successfully"},
        status.HTTP_409_CONFLICT: {"description": "Role already exists with the given name"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Get Single Role
# ============================================================
GET_ROLE_DOCS = {
    "summary": "Get role details",
    "description": "Fetch detailed information for a specific role by role_id.",
    "responses": {
        status.HTTP_200_OK: {"description": "Role found"},
        status.HTTP_404_NOT_FOUND: {"description": "Role not found"},
    },
}

# ============================================================
# List Roles
# ============================================================
LIST_ROLES_DOCS = {
    "summary": "List roles",
    "description": (
        "Returns a paginated list of roles. "
        "`skip` controls the offset and `limit` controls the number of results."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Roles fetched successfully"},
    },
}

# ============================================================
# Update Role
# ============================================================
UPDATE_ROLE_DOCS = {
    "summary": "Update a role",
    "description": (
        "Updates role fields by role_id. Role name must remain unique across all roles."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Role updated successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Role not found"},
        status.HTTP_409_CONFLICT: {"description": "Role with this name already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Delete Role
# ============================================================
DELETE_ROLE_DOCS = {
    "summary": "Delete a role",
    "description": (
        "Deletes a role by role_id. "
        "Depending on system logic, this can be soft-delete or permanent delete."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Role deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Role not found"},
    },
}
