"""
File: app/api/v1/routes/docs/role_permission.py
OpenAPI documentation for RolePermission API endpoints.
"""

from fastapi import status

# ============================================================
# Create RolePermission Assignment
# ============================================================
CREATE_ROLE_PERMISSION_DOCS = {
    "summary": "Assign a permission to a role",
    "description": (
        "Creates a new RolePermission assignment. A role cannot receive the same permission "
        "more than once; attempting to assign an existing mapping will return a conflict error."
    ),
    "responses": {
        status.HTTP_201_CREATED: {"description": "RolePermission created successfully"},
        status.HTTP_409_CONFLICT: {"description": "RolePermission assignment already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Get Single RolePermission
# ============================================================
GET_ROLE_PERMISSION_DOCS = {
    "summary": "Get role-permission assignment",
    "description": (
        "Fetches details of a RolePermission assignment by ID. "
        "The response contains both the role ID and permission ID."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "RolePermission retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "RolePermission not found"},
    },
}

# ============================================================
# List RolePermission Assignments
# ============================================================
LIST_ROLE_PERMISSIONS_DOCS = {
    "summary": "List role-permission assignments",
    "description": (
        "Returns a paginated list of all RolePermission mappings. "
        "`skip` specifies the starting offset, and `limit` controls the number of results."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "RolePermissions listed successfully"},
    },
}

# ============================================================
# Delete RolePermission Assignment
# ============================================================
DELETE_ROLE_PERMISSION_DOCS = {
    "summary": "Delete a role-permission assignment",
    "description": (
        "Deletes a RolePermission mapping by ID. This removes the permission from the role."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "RolePermission deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "RolePermission not found"},
    },
}
