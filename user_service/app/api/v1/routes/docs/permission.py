"""
File: app/api/v1/routes/docs/permission.py
OpenAPI documentation for Permission API endpoints.
"""

from fastapi import status

# ============================================================
# Create Permission
# ============================================================
CREATE_PERMISSION_DOCS = {
    "summary": "Create a new permission",
    "description": (
        "Creates a new permission. Permission names must be unique. "
        "If a permission with the same name already exists, a conflict error is returned."
    ),
    "responses": {
        status.HTTP_201_CREATED: {"description": "Permission created successfully"},
        status.HTTP_409_CONFLICT: {"description": "Permission already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Get Single Permission
# ============================================================
GET_PERMISSION_DOCS = {
    "summary": "Get permission details",
    "description": "Fetches detailed information for a specific permission by its ID.",
    "responses": {
        status.HTTP_200_OK: {"description": "Permission retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Permission not found"},
    },
}

# ============================================================
# List Permissions
# ============================================================
LIST_PERMISSIONS_DOCS = {
    "summary": "List permissions",
    "description": (
        "Returns a paginated list of permissions. "
        "`skip` defines the offset and `limit` defines maximum number of records per page."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Permissions listed successfully"},
    },
}

# ============================================================
# Update Permission
# ============================================================
UPDATE_PERMISSION_DOCS = {
    "summary": "Update permission",
    "description": (
        "Updates permission attributes. Permission name must remain unique across the system."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Permission updated successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Permission not found"},
        status.HTTP_409_CONFLICT: {"description": "Permission with this name already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Delete Permission
# ============================================================
DELETE_PERMISSION_DOCS = {
    "summary": "Delete permission",
    "description": (
        "Deletes a permission by its ID. "
        "Depending on system design, this can be permanent or soft deletion."
    ),
    "responses": {
        status.HTTP_200_OK: {"description": "Permission deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Permission not found"},
    },
}
