"""
File: app/api/v1/routes/docs/user_roles.py
OpenAPI documentation for UserRole API endpoints.
"""

from fastapi import status

# ============================================================
# Create UserRole Assignment
# ============================================================
CREATE_USER_ROLE_DOCS = {
    "summary": "Assign a role to a user",
    "description": (
        "Creates a new UserRole assignment. A user can only be assigned the same "
        "role once; attempting to assign a duplicate combination will return a conflict error."
    ),
    "responses": {
        status.HTTP_201_CREATED: {"description": "UserRole created successfully"},
        status.HTTP_409_CONFLICT: {"description": "UserRole assignment already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Get Single UserRole
# ============================================================
GET_USER_ROLE_DOCS = {
    "summary": "Get UserRole assignment",
    "description": (
        "Fetches the details of a UserRole assignment by its ID. "
        "This includes both the user ID and the role ID."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "UserRole retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "UserRole not found"},
    },
}

# ============================================================
# List UserRole Assignments
# ============================================================
LIST_USER_ROLES_DOCS = {
    "summary": "List user-role assignments",
    "description": (
        "Returns a paginated list of all UserRole assignments. "
        "`skip` defines offset, and `limit` defines page size."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "UserRoles listed successfully"},
    },
}

# ============================================================
# Delete UserRole Assignment
# ============================================================
DELETE_USER_ROLE_DOCS = {
    "summary": "Delete a user-role assignment",
    "description": (
        "Deletes a UserRole assignment by its ID. This will remove the role from the user."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "UserRole deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "UserRole not found"},
    },
}
