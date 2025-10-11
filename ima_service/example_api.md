
# IMA API's
## Auth & Session Management
Base path: `/api/v1`

### POST /api/v1/auth/register
Register a new user (tenant-scoped). Public endpoint.

Request JSON:

```json
{
  "email": "alice@example.com",
  "password": "Str0ngP@ssw0rd!",
  "full_name": "Alice Example",
  "tenant_id": "t_001"
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "id": "u_0a1b2c3d",
    "email": "alice@example.com",
    "full_name": "Alice Example",
    "tenant_id": "t_001",
    "is_active": true,
    "created_at": "2025-10-11T12:00:00Z"
  },
  "meta": {"request_id": "req_register_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

Errors:
- 422 Validation error (missing fields)
- 409 Conflict (email already exists)

---

### POST /api/v1/auth/login
Authenticate and receive access + refresh tokens. Public endpoint.

Request JSON:

```json
{
  "email": "alice@example.com",
  "password": "Str0ngP@ssw0rd!"
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "access_token": "<JWT_ACCESS_TOKEN>",
    "refresh_token": "<REFRESH_TOKEN>",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "u_0a1b2c3d",
      "email": "alice@example.com",
      "full_name": "Alice Example",
      "tenant_id": "t_001",
      "roles": ["tenant_admin"],
      "permissions": ["manage_users","view_tenants"]
    }
  },
  "meta": {"request_id": "req_login_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

Errors:
- 401 Unauthorized (invalid credentials)
- 423 Locked (user disabled)

---

### POST /api/v1/auth/refresh
Exchange refresh token for a new access token.

Request JSON:

```json
{
  "refresh_token": "<REFRESH_TOKEN>"
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "access_token": "<NEW_JWT_ACCESS_TOKEN>",
    "expires_in": 900
  },
  "meta": {"request_id": "req_refresh_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

Errors:
- 401 Invalid or revoked refresh token

---

### POST /api/v1/auth/logout
Invalidate refresh token (requires Authorization header)

Request JSON:

```json
{
  "refresh_token": "<REFRESH_TOKEN>"
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {"message": "Logged out"},
  "meta": {"request_id": "req_logout_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

## Users

### GET /api/v1/me
Get authenticated user info.

Headers: Authorization: Bearer <ACCESS_TOKEN>

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "id": "u_0a1b2c3d",
    "email": "alice@example.com",
    "full_name": "Alice Example",
    "tenant_id": "t_001",
    "roles": ["tenant_admin"],
    "permissions": ["manage_users","view_tenants"],
    "created_at": "2025-10-11T12:00:00Z"
  },
  "meta": {"request_id": "req_me_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### GET /api/v1/users
List users in the caller's tenant (paginated).

Query params: ?page=1&size=20&search=alice

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "u_0a1b2c3d",
        "email": "alice@example.com",
        "full_name": "Alice Example",
        "tenant_id": "t_001",
        "roles": ["tenant_admin"],
        "is_active": true,
        "created_at": "2025-10-01T09:12:34Z"
      },
      {
        "id": "u_0b2c3d4e",
        "email": "bob@example.com",
        "full_name": "Bob Example",
        "tenant_id": "t_001",
        "roles": ["viewer"],
        "is_active": true,
        "created_at": "2025-09-22T16:20:00Z"
      }
    ],
    "page": 1,
    "size": 20,
    "total": 2
  },
  "meta": {"request_id": "req_list_users_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

Errors:
- 403 Forbidden (if user lacks permission)

---

### GET /api/v1/users/{id}
Get a single user (tenant-scoped).

200 OK — Response (full realistic):

```json
{
  "success": true,
  "data": {
    "id": "u_0a1b2c3d",
    "email": "alice@example.com",
    "full_name": "Alice Example",
    "tenant_id": "t_001",
    "roles": ["tenant_admin"],
    "permissions": ["manage_users","view_tenants"],
    "is_active": true,
    "created_at": "2025-10-01T09:12:34Z",
    "last_login_at": "2025-10-11T11:50:00Z"
  },
  "meta": {"request_id": "req_get_user_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### POST /api/v1/users
Create user (requires manage_users permission)

Request JSON:

```json
{
  "email": "charlie@example.com",
  "full_name": "Charlie Example",
  "password": "An0ther$trongP4ss",
  "roles": ["viewer"],
  "tenant_id": "t_001"
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "id": "u_0c3d4e5f",
    "email": "charlie@example.com",
    "full_name": "Charlie Example",
    "tenant_id": "t_001",
    "roles": ["viewer"],
    "created_at": "2025-10-11T12:00:00Z"
  },
  "meta": {"request_id": "req_create_user_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### PATCH /api/v1/users/{id}
Update user (partial). Requires permission.

Request JSON (example):

```json
{
  "full_name": "Alice Newname",
  "roles": ["manager"]
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "id": "u_0a1b2c3d",
    "email": "alice@example.com",
    "full_name": "Alice Newname",
    "roles": ["manager"],
    "updated_at": "2025-10-11T12:00:00Z"
  },
  "meta": {"request_id": "req_patch_user_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### DELETE /api/v1/users/{id}
Soft delete user (set deleted_at). Requires manage_users.

204 No Content — Response (empty success):

```json
{
  "success": true,
  "data": null,
  "meta": {"request_id": "req_delete_user_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

## Roles & Permissions

### GET /api/v1/roles
List roles (paginated).

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "r_admin",
        "name": "tenant_admin",
        "description": "Full tenant-level admin",
        "tenant_id": "t_001",
        "is_system_role": false,
        "created_at": "2025-09-01T08:00:00Z"
      },
      {
        "id": "r_viewer",
        "name": "viewer",
        "description": "Read-only role",
        "tenant_id": "t_001",
        "is_system_role": false,
        "created_at": "2025-09-02T08:00:00Z"
      }
    ],
    "page": 1,
    "size": 20,
    "total": 2
  },
  "meta": {"request_id": "req_list_roles_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### POST /api/v1/roles
Create a new role (requires admin permission)

Request JSON:

```json
{
  "name": "manager",
  "description": "Team manager",
  "tenant_id": "t_001",
  "is_system_role": false
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "id": "r_mgr01",
    "name": "manager",
    "description": "Team manager",
    "tenant_id": "t_001",
    "is_system_role": false,
    "created_at": "2025-10-11T12:00:00Z"
  },
  "meta": {"request_id": "req_create_role_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### POST /api/v1/roles/{id}/permissions
Assign permissions to a role.

Request JSON:

```json
{
  "permissions": ["manage_users","view_tenants"]
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "role_id": "r_mgr01",
    "permissions": ["manage_users","view_tenants"]
  },
  "meta": {"request_id": "req_assign_perm_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### GET /api/v1/permissions
List all permissions.

200 OK — Response:

```json
{
  "success": true,
  "data": [
    {"id": "p_manage_users", "code": "manage_users", "description": "Create/update/delete users"},
    {"id": "p_view_tenants", "code": "view_tenants", "description": "View tenant metadata"}
  ],
  "meta": {"request_id": "req_list_perms_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

## Audit & Sessions

### GET /api/v1/sessions
List active sessions for user (requires auth)

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {"id": "sess_01", "user_id": "u_0a1b2c3d", "created_at": "2025-10-11T11:00:00Z", "expires_at": "2025-10-11T12:00:00Z"}
    ],
    "page": 1,
    "size": 10,
    "total": 1
  },
  "meta": {"request_id": "req_list_sessions_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

### GET /api/v1/audit/logs
Fetch audit logs (requires view_audit permission; paginated)

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {"id": 1001, "user_id": "u_0a1b2c3d", "tenant_id": "t_001", "action": "POST /api/v1/users", "status_code": 201, "timestamp": "2025-10-11T12:00:00Z"}
    ],
    "page": 1,
    "size": 20,
    "total": 1
  },
  "meta": {"request_id": "req_audit_01", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---

## Error Examples (standardized)

- 401 Unauthorized

```json
{
  "success": false,
  "error": {"code": "unauthorized", "message": "Missing or invalid Authorization header"},
  "meta": {"request_id": "req_err_401", "timestamp": "2025-10-11T12:00:00Z"}
}
```

- 403 Forbidden

```json
{
  "success": false,
  "error": {"code": "forbidden", "message": "Insufficient permissions to access resource"},
  "meta": {"request_id": "req_err_403", "timestamp": "2025-10-11T12:00:00Z"}
}
```

- 404 Not Found

```json
{
  "success": false,
  "error": {"code": "not_found", "message": "User not found"},
  "meta": {"request_id": "req_err_404", "timestamp": "2025-10-11T12:00:00Z"}
}
```

- 422 Validation Error

```json
{
  "success": false,
  "error": {"code": "validation_error", "message": "email is required"},
  "meta": {"request_id": "req_err_422", "timestamp": "2025-10-11T12:00:00Z"}
}
```

---
