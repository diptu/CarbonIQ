"""
Role endpoint documentation.
"""

LIST_ROLES = {
    "summary": "List all roles",
    "description": """Retrieve a list of all roles in the system.

**What you get**:
- List of roles with `id`, `name`, `description`, `is_system` flag

**Example request**:

GET /roles/
No request body needed.
```""",
}

CREATE_ROLE = {
    "summary": "Create a new role",
    "description": """Create a new role in the system.

**What you need to provide**:
- `name`: Unique name for the role
- `description`: Optional description
- `is_system`: Optional flag for system roles (default `False`)

**What you get**:
- Created role details

**Errors**:
- 400 Bad Request if role with the same name already exists

**Example request**:

POST /roles/
```json
{
    "name": "ADMIN",
    "description": "Administrator role",
    "is_system": false
}
```""",
}
