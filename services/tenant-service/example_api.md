
# Tenant Service API Examples

Base path: `/api/v1`

## Organizations

### POST /api/v1/organizations
Create a new organization. Requires super_admin.

Request JSON:

```json
{
  "name": "Acme Corp",
  "domain": "acme.com",
  "owner_user_id": "u_0a1b2c3d"
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "id": "org_001",
    "name": "Acme Corp",
    "domain": "acme.com",
    "owner_user_id": "u_0a1b2c3d",
    "status": "active",
    "created_at": "2025-10-11T09:38:31.068584Z"
  },
  "meta": {"request_id": "req_create_org_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

Errors:
- 403 Forbidden (not super_admin)
- 422 Validation error

---

## Tenants

### POST /api/v1/tenants
Create a tenant under organization. Requires manage_tenant permission.

Request JSON:

```json
{
  "name": "Acme Tenant 1",
  "organization_id": "org_001",
  "parent_tenant_id": null,
  "plan": "standard",
  "owner_user_id": "u_0a1b2c3d",
  "config": {}
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "id": "t_001",
    "name": "Acme Tenant 1",
    "organization_id": "org_001",
    "parent_tenant_id": null,
    "plan": "standard",
    "owner_user_id": "u_0a1b2c3d",
    "status": "active",
    "config": {},
    "created_at": "2025-10-11T09:38:31.068584Z"
  },
  "meta": {"request_id": "req_create_tenant_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

Errors:
- 403 Forbidden (insufficient permissions)
- 422 Validation error

---

### GET /api/v1/tenants
List tenants (paginated).

Query params: ?page=1&size=20&search=Acme

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "t_001",
        "name": "Acme Tenant 1",
        "organization_id": "org_001",
        "parent_tenant_id": null,
        "plan": "standard",
        "status": "active",
        "owner_user_id": "u_0a1b2c3d",
        "created_at": "2025-10-11T09:38:31.068584Z"
      }
    ],
    "page": 1,
    "size": 20,
    "total": 1
  },
  "meta": {"request_id": "req_list_tenants_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### GET /api/v1/tenants/{id}
Get tenant details.

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "id": "t_001",
    "name": "Acme Tenant 1",
    "organization_id": "org_001",
    "parent_tenant_id": null,
    "plan": "standard",
    "status": "active",
    "owner_user_id": "u_0a1b2c3d",
    "config": {},
    "created_at": "2025-10-11T09:38:31.068584Z"
  },
  "meta": {"request_id": "req_get_tenant_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### PATCH /api/v1/tenants/{id}
Update tenant.

Request JSON:

```json
{
  "name": "Acme Tenant 1 Updated",
  "plan": "premium"
}
```

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "id": "t_001",
    "name": "Acme Tenant 1 Updated",
    "plan": "premium",
    "updated_at": "2025-10-11T09:38:31.068584Z"
  },
  "meta": {"request_id": "req_patch_tenant_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### DELETE /api/v1/tenants/{id}
Soft delete tenant. Requires manage_tenant permission.

204 No Content — Response:

```json
{
  "success": true,
  "data": null,
  "meta": {"request_id": "req_delete_tenant_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### GET /api/v1/tenants/{id}/hierarchy
Get tenant hierarchy tree.

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "id": "t_001",
    "name": "Acme Tenant 1",
    "children": []
  },
  "meta": {"request_id": "req_hierarchy_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

## Tenant Users

### GET /api/v1/tenants/{id}/users
List users in tenant (paginated).

200 OK — Response:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "user_id": "u_0a1b2c3d",
        "roles": ["tenant_admin"],
        "joined_at": "2025-10-11T09:38:31.068584Z"
      }
    ],
    "page": 1,
    "size": 20,
    "total": 1
  },
  "meta": {"request_id": "req_list_tenant_users_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### POST /api/v1/tenants/{id}/users
Assign/invite user to tenant. Requires manage_users permission.

Request JSON:

```json
{
  "user_id": "u_0b2c3d4e",
  "roles": ["viewer"]
}
```

201 Created — Response:

```json
{
  "success": true,
  "data": {
    "tenant_id": "t_001",
    "user_id": "u_0b2c3d4e",
    "roles": ["viewer"],
    "joined_at": "2025-10-11T09:38:31.068584Z"
  },
  "meta": {"request_id": "req_add_tenant_user_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

---

### DELETE /api/v1/tenants/{id}/users/{user_id}
Remove user from tenant.

204 No Content — Response:

```json
{
  "success": true,
  "data": null,
  "meta": {"request_id": "req_remove_tenant_user_01", "timestamp": "2025-10-11T09:38:31.068584Z"}
}
```

