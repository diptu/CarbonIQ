"""
File: app/api/v1/docs_user.py
OpenAPI documentation for User endpoints.
"""

from fastapi import status

# ============================================================
# Create User
# ============================================================
CREATE_USER_DOCS = {
    "summary": "Create a new user",
    "description": "Create a new user record in the database.",
    "responses": {
        status.HTTP_201_CREATED: {"description": "User created successfully"},
        status.HTTP_409_CONFLICT: {"description": "User with this email already exists"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# List Users
# ============================================================
LIST_USERS_DOCS = {
    "summary": "List users",
    "description": "Retrieve a paginated list of users.",
    "responses": {
        status.HTTP_200_OK: {"description": "Users fetched successfully"},
    },
}

# ============================================================
# Verify User
# ============================================================
VERIFY_USER_DOCS = {
    "summary": "Verify user login credentials",
    "description": "Validates email and password, returns user with roles and permissions.",
    "responses": {
        status.HTTP_200_OK: {"description": "User verified"},
        status.HTTP_400_BAD_REQUEST: {"description": "Missing email or password"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
    },
}

# ============================================================
# Get User
# ============================================================
GET_USER_DOCS = {
    "summary": "Get user details",
    "description": "Retrieve user info by user_id.",
    "responses": {
        status.HTTP_200_OK: {"description": "User found"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
}

# ============================================================
# Update User
# ============================================================
UPDATE_USER_DOCS = {
    "summary": "Update user",
    "description": "Update user profile fields.",
    "responses": {
        status.HTTP_200_OK: {"description": "User updated successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
}

# ============================================================
# Delete User
# ============================================================
DELETE_USER_DOCS = {
    "summary": "Delete user",
    "description": "Soft-delete user or permanently remove user based on system logic.",
    "responses": {
        status.HTTP_200_OK: {"description": "User deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
}

# ============================================================
# Activate User
# ============================================================
ACTIVATE_USER_DOCS = {
    "summary": "Activate user",
    "description": "Set user status to active.",
    "responses": {
        status.HTTP_200_OK: {"description": "User activated"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
}

# ============================================================
# Deactivate User
# ============================================================
DEACTIVATE_USER_DOCS = {
    "summary": "Deactivate user",
    "description": "Set user status to inactive.",
    "responses": {
        status.HTTP_200_OK: {"description": "User deactivated"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
}
