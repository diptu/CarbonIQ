
# Tenant Service

For a multi-tenant, hierarchical database–backed RBAC (Role-Based Access Control) system

## Overview
The Tenant Service manages organizations, tenants, hierarchical relationships, tenant metadata, and configuration. It enforces tenant scoping and integrates with the IMA Service for authentication and RBAC enforcement.

## ⚙️ System Overview

Architecture:

Multi-tenant hierarchy: Organization > Tenant > Subtenant (optional) > User

RBAC: Role & Permission-based with inheritance (roles → permissions)

DB: PostgreSQL (schemas or row-based tenancy)

Services:

IMA Service → Handles authentication, authorization, users, roles, permissions

Tenant Service → Manages tenant creation, hierarchy, and metadata

API Style: REST (JSON responses)

Auth: JWT + Refresh Token (issued by IMA Service)


## 🔐 Key Features
- Tenant creation, update, and soft deletion
- Hierarchical tenant management
- Tenant-scoped user assignment
- Integration with IMA Service for RBAC enforcement
- Paginated endpoints for scalability

---

## 🗂️ Core Entities

| Entity | Description |
|---------|--------------|
| **Organization** | Top-level organization grouping tenants |
| **Tenant** | Represents a tenant or subtenant |
| **TenantUser** | User assigned to a tenant with roles |
| **TenantConfig** | Tenant-specific configuration (optional JSON) |

---
## 🗂️ Tables

1. organizations

| Column          | Type        | Description           |
| --------------- | ----------- | -------------------- |
| `id`            | UUID (PK)  | Organization ID      |
| `name`          | VARCHAR(255)| Organization name    |
| `domain`        | VARCHAR(255)| Domain               |
| `owner_user_id` | UUID (FK → users.id) | Owner user |
| `status`        | VARCHAR(50)| active/inactive      |
| `created_at`    | TIMESTAMP   | Creation timestamp   |
| `updated_at`    | TIMESTAMP   | Last update timestamp|

2. tenants

| Column            | Type        | Description |
| ----------------- | ----------- | ----------- |
| `id`              | UUID (PK)  | Tenant ID   |
| `name`            | VARCHAR(255)| Tenant name |
| `organization_id` | UUID (FK → organizations.id)| Parent org |
| `parent_tenant_id`| UUID (nullable FK → tenants.id) | Optional parent tenant |
| `plan`            | VARCHAR(50)| Subscription plan |
| `status`          | VARCHAR(50)| active/inactive |
| `owner_user_id`   | UUID (FK → users.id) | Owner user |
| `config`          | JSONB       | Tenant configs |
| `created_at`      | TIMESTAMP   | Creation timestamp |
| `updated_at`      | TIMESTAMP   | Last update timestamp |

3. tenant_users

| Column     | Type           | Description |
| ---------- | -------------- | ----------- |
| `tenant_id`| UUID (FK → tenants.id) | Tenant reference |
| `user_id`  | UUID (FK → users.id) | User reference |
| `roles`    | JSONB           | Roles assigned in this tenant |
| `joined_at`| TIMESTAMP       | Join timestamp |
| PRIMARY KEY| (`tenant_id`,`user_id`) | Composite key |

---

| Method     | Endpoint                                 | Description                                | Auth Required |
| ---------- | ---------------------------------------- | ------------------------------------------ | ------------- |
| **POST**   | `/api/v1/tenants`                        | Create tenant                              | ✅ (manage_tenant) |
| **GET**    | `/api/v1/tenants`                        | List tenants (paginated)                   | ✅             |
| **GET**    | `/api/v1/tenants/{id}`                 | Get tenant details                          | ✅             |
| **PATCH**  | `/api/v1/tenants/{id}`                 | Update tenant                               | ✅ (update_tenant) |
| **DELETE** | `/api/v1/tenants/{id}`                 | Soft delete tenant                          | ✅ (manage_tenant) |
| **GET**    | `/api/v1/tenants/{id}/hierarchy`       | Get tenant hierarchy tree                   | ✅             |
| **GET**    | `/api/v1/tenants/{id}/users`           | List users in tenant (paginated)           | ✅ (view_users) |
| **POST**   | `/api/v1/tenants/{id}/users`           | Assign/invite user to tenant               | ✅ (manage_users) |
| **DELETE** | `/api/v1/tenants/{id}/users/{user_id}`| Remove user from tenant                     | ✅ (manage_users) |
| **POST**   | `/api/v1/organizations`                  | Create organization                          | ✅ (super_admin) |

---

🚀 Strategy Overview

We'll combine token-based authentication, tenant-context enforcement, and RBAC middleware:

```text
[Client] → [API Gateway] → [Auth Middleware] → [Tenant Service]
                                  ↓
                          [IMA (Auth Service)]
```

🧠 Objective

Ensure only authenticated users can call Tenant Service APIs,
and their access is scoped to their tenant hierarchy and RBAC roles.

1. Use JWT from the IMA Service (Central Auth Provider)

All authentication happens in the IMA Service (Identity Management API).

When user logs in:

They get an Access Token (JWT) and Refresh Token.

The JWT includes claims like:

```json
{
  "sub": "u_12345",
  "tenant_id": "t_001",
  "roles": ["tenant_admin"],
  "permissions": ["manage_users", "view_tenants"],
  "exp": 1728902400,
  "iss": "ima.service.local"
}
```

2. Audit and Logging
   
| Field     | Example                   |
| --------- | ------------------------- |
| user_id   | u_12345                   |
| tenant_id | t_001                     |
| endpoint  | /api/v1/tenants/001/users |
| action    | GET                       |
| status    | 200                       |
| timestamp | 2025-10-11T09:35:38.106840Z               |


3. 🧩 Bonus: Advanced Hardening

Rotate signing keys (JWKS) regularly.

Deny access by default (zero-trust model).

Multi-tenant DB filters via ORM decorators.

JWT caching for performance (e.g., Redis token verifier).

Use OPA (Open Policy Agent) or Casbin if policies become complex.

