# ima_service/app/api/v1/docs.py

CREATE_USER = {
    "summary": "Create a new user",
    "description": """Create a new user in the system.  
The new user will automatically get the default role: VIEWER.

**What you need to provide**:
- Email address
- Password
- Active status (yes/no)
- Admin rights (yes/no)

**What you get**:
- The details of the new user
- Their assigned roles

**Example request**:

POST /users/
```json
{
    "email": "jane.doe@example.com",
    "password": "SecurePass123",
    "is_active": true,
    "is_superuser": false
}
```""",
}

UPDATE_USER = {
    "summary": "Update user information",
    "description": """Update the email, password, or admin status of an existing user.

**What you can change**:
- Email address
- Password
- Active status
- Admin rights

**What you get**:
- Updated user details
- Assigned roles remain unchanged

**Example request**:

PUT /users/{user_id}/
```json
{
    "email": "new.email@example.com",
    "password": "NewSecurePass123",
    "is_active": true,
    "is_superuser": false
}
```""",
}

DELETE_USER = {
    "summary": "Delete a user",
    "description": """Permanently delete a user account from the system.

**What happens**:
- The user is removed
- Their roles are also removed

**Example request**:

DELETE /users/{user_id}/
No request body needed.
""",
}

DEACTIVATE_USER = {
    "summary": "Deactivate a user",
    "description": """Temporarily deactivate a user account.  
Deactivated users cannot log in but are not deleted.

**Example request**:

POST /users/{user_id}/deactivate
No request body needed.
""",
}

REACTIVATE_USER = {
    "summary": "Reactivate a user",
    "description": """Reactivate a previously deactivated user account.  
The user will regain access with their existing roles.

**Example request**:

POST /users/{user_id}/reactivate
No request body needed.
""",
}

ASSIGN_ROLE = {
    "summary": "Assign a role to a user",
    "description": """Assign or update a role for a user. Optionally, you can specify a tenant.  

**What you need**:
- Role to assign (e.g., VIEWER, ADMIN)
- Optional tenant ID for multi-tenant setups

**What you get**:
- Updated user roles

**Example request**:

POST /users/{user_id}/roles?role_name=VIEWER
```json
{
    "tenant_id": "optional-tenant-uuid"
}
```""",
}

LIST_USERS = {
    "summary": "List all users",
    "description": """Retrieve a list of users with pagination.

**Optional query parameters**:
- `skip`: Number of records to skip (default 0)
- `limit`: Number of records to return (default 10, max 100)

**What you get**:
- List of users
- Pagination info (first, previous, next, last pages)

**Example request**:

GET /users/?skip=0&limit=10
No request body needed.
```""",
}

GET_USER_BY_ID = {
    "summary": "Get a user by ID",
    "description": """Retrieve a single user from the system by their unique ID (UUID).

**What you need to provide**:
- The user ID in the URL path

**What you get**:
- User details including assigned roles

**Example request**:

GET /users/{user_id}
No request body needed.

**Example response**:
```json
{
    "statusCode": 200,
    "msg": "User retrieved successfully",
    "details": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "jane.doe@example.com",
        "is_active": true,
        "is_superuser": false,
        "roles": ["VIEWER"]
    }
}
```""",
}
