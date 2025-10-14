# IMA Service (Identity & Management API)

For a multi-tenant, hierarchical database–backed RBAC (Role-Based Access Control) system

## Overview
The IMA Service is responsible for authentication, authorization, role & permission management, and session lifecycle. It issues RS256-signed JWTs and provides endpoints for user and role management used by Tenant Service and other microservices.

## Tenant Management

### Tenant ID Source
The `tenant_id` in IMA Service does **not** come from an internal table.  
Instead, it is **fetched from the Tenant Service**, which is hosted in a **separate database**.

Whenever a new user or request is processed, IMA Service communicates with the Tenant Service to identify the correct tenant.

---

## Automatic Tenant Resolution via Subdomain

Each tenant is identified automatically based on the request’s subdomain.

**Example:**
```
https://acme.carboniq.ai/api/v1/users
```
Here, the subdomain `acme` maps to a specific tenant record in the Tenant Service.  
IMA Service sends the subdomain to the Tenant Service API to retrieve the associated `tenant_id`.

**Tenant Service Endpoint Example:**
```
GET /tenant-service/api/v1/tenants/resolve?subdomain=acme
Response:
{
  "tenant_id": "77ed9f5e-12e9-430d-bada-fa6efa24e68d",
  "name": "Acme Corp",
  "domain": "acme.carboniq.ai"
}
```

---

## Sequence Flow

### 1. User Request Arrives
A request (e.g., `/api/v1/users/login`) comes in via subdomain `acme.carboniq.ai`.

### 2. Tenant Resolution
IMA Service extracts the subdomain (`acme`) and calls Tenant Service:
```
GET /tenant-service/api/v1/tenants/resolve?subdomain=acme
```

### 3. Tenant Validation
Tenant Service responds with the `tenant_id` and other metadata.

### 4. User Operation
IMA Service uses the `tenant_id` from Tenant Service to perform the requested operation (e.g., user authentication, user listing).

### 5. Multi-Tenant Data Isolation
All user-related operations in IMA Service are scoped by the resolved `tenant_id` to ensure strict data isolation.

---

## Example Flow Diagram

```
+-------------+          +----------------+          +------------------+
| User Client |  --->    | IMA Service    |  --->    | Tenant Service   |
| (acme.carboniq.ai)     | (extract subdomain)       | (resolve tenant) |
+-------------+          +----------------+          +------------------+
                               | tenant_id |
                               v
                         [Process user ops]
```

---

## Summary

- **Tenant IDs** are managed by **Tenant Service**.  
- IMA Service performs **automatic subdomain-based tenant resolution**.  
- Ensures **data isolation and secure cross-service communication**.



## ⚙️ System Overview

Architecture:

Multi-tenant hierarchy: Organization > Tenant > Subtenant (optional) > User

RBAC: Role & Permission-based with inheritance (roles → permissions)

DB: PostgreSQL (schemas or row-based tenancy)

Services:

IMA Service → Handles authentication, authorization, users, roles, permissions

Tenant Service → Manages tenant creation, hierarchy, and metadata

API Style: REST (JSON responses)

Auth: JWT + Refresh Token, integrated with role-based policy middleware


## 🔐 Key Features
- JWT-based authentication (RS256)
- Multi-tenant aware user management
- Role & permission-based access control (RBAC)
- Refresh token lifecycle management
- Integration-ready with Tenant Service
- Optional audit logging & policy engine (Casbin/OPA)

---

## 🗂️ Core Entities

| Entity | Description |
|---------|--------------|
| **User** | Represents an authenticated individual tied to a tenant |
| **Role** | Defines access level and permissions for a tenant or system |
| **Permission** | Atomic operation that can be assigned to roles |
| **UserRole** | Many-to-many relationship between users and roles |
| **RolePermission** | Many-to-many relationship between roles and permissions |
| **AuthToken** | Refresh/session token tracking |
| **AuditLog** | Records every privileged or sensitive action |

---
## 🗂️ Tables

1. users
   
| Column          | Type                                  | Description           |
| --------------- | ------------------------------------- | --------------------- |
| `id`            | UUID (PK)                             | Unique user ID        |
| `email`         | VARCHAR(255) NOT NULL, UNIQUE                  | User email (login ID) |
| `password_hash` | TEXT                                  | Hashed password       |
| `full_name`     | VARCHAR(255)                          | Display name          |
| `is_active`     | BOOLEAN                               | Account status        |
| `tenant_id`     | UUID (FK → tenant_service.tenants.id) | User’s tenant context |
| `created_at`    | TIMESTAMP                             | Created time          |
| `updated_at`    | TIMESTAMP                             | Updated time          |

⚠️ The tenant_id defines which tenant the user belongs to,
but their access level is determined by their roles.

2. roles

| Column           | Type            | Description                                 |
| ---------------- | --------------- | ------------------------------------------- |
| `id`             | UUID (PK)       | Unique role ID                              |
| `name`           | VARCHAR(100)    | Role name (`tenant_admin`, `manager`, etc.) |
| `description`    | TEXT            | Human-readable description                  |
| `tenant_id`      | UUID (nullable) | Role scope (null = global/system role)      |
| `is_system_role` | BOOLEAN         | If true, accessible to all tenants          |
| `created_at`     | TIMESTAMP       | Created time                                |

Roles can be system-wide (like super_admin) or tenant-specific (like tenant_admin).

3. permissions

| Column        | Type                 | Description                                          |
| ------------- | -------------------- | ---------------------------------------------------- |
| `id`          | UUID (PK)            | Permission ID                                        |
| `code`        | VARCHAR(100), UNIQUE | Permission code (`manage_users`, `view_tenant`)      |
| `description` | TEXT                 | Description                                          |
| `module`      | VARCHAR(50)          | Optional grouping (e.g. `tenant`, `user`, `billing`) |

4. role_permissions

| Column          | Type                         | Description     |
| --------------- | ---------------------------- | --------------- |
| `role_id`       | UUID (FK → roles.id)         | Role link       |
| `permission_id` | UUID (FK → permissions.id)   | Permission link |
| PRIMARY KEY     | (`role_id`, `permission_id`) | Composite key   |

Defines role → permission mapping.


5. user_roles

| Column      | Type                   | Description   |
| ----------- | ---------------------- | ------------- |
| `user_id`   | UUID (FK → users.id)   | User link     |
| `role_id`   | UUID (FK → roles.id)   | Role link     |
| PRIMARY KEY | (`user_id`, `role_id`) | Composite key |

Defines user → role assignments

6. auth_tokens (for refresh tokens / sessions)

| Column       | Type                 | Description            |
| ------------ | -------------------- | ---------------------- |
| `id`         | UUID (PK)            | Token ID               |
| `user_id`    | UUID (FK → users.id) | Associated user        |
| `token`      | TEXT                 | Refresh token (hashed) |
| `expires_at` | TIMESTAMP            | Expiry                 |
| `revoked`    | BOOLEAN              | If token invalidated   |


7. audit_logs

| Column        | Type           | Description                              |
| ------------- | -------------- | ---------------------------------------- |
| `id`          | BIGSERIAL (PK) | Log ID                                   |
| `user_id`     | UUID           | Actor                                    |
| `tenant_id`   | UUID           | Tenant context                           |
| `action`      | VARCHAR(100)   | Action performed                         |
| `resource`    | VARCHAR(100)   | Target resource (e.g. `/api/v1/tenants`) |
| `status_code` | INT            | HTTP status                              |
| `timestamp`   | TIMESTAMP      | Event time                               |


---
| Method     | Endpoint                         | Description                   | Auth Required |
| ---------- | -------------------------------- | ----------------------------- | ------------- |
| **POST**   | `/api/v1/auth/register`          | Register a new user           | ❌             |
| **POST**   | `/api/v1/auth/login`             | Login and get tokens          | ❌             |
| **POST**   | `/api/v1/auth/refresh`           | Refresh JWT token             | ✅             |
| **POST**   | `/api/v1/auth/logout`            | Logout user                   | ✅             |
| **GET**    | `/api/v1/users`                  | List users (tenant scoped)    | ✅ (admin)     |
| **GET**    | `/api/v1/users/{id}`             | Get user details              | ✅             |
| **POST**   | `/api/v1/users`                  | Create user under tenant      | ✅ (admin)     |
| **PATCH**  | `/api/v1/users/{id}`             | Update user profile or role   | ✅             |
| **DELETE** | `/api/v1/users/{id}`             | Soft delete user              | ✅ (admin)     |
| **GET**    | `/api/v1/roles`                  | List all roles in tenant      | ✅             |
| **POST**   | `/api/v1/roles`                  | Create a role                 | ✅ (admin)     |
| **PATCH**  | `/api/v1/roles/{id}`             | Update role                   | ✅ (admin)     |
| **DELETE** | `/api/v1/roles/{id}`             | Delete role                   | ✅ (admin)     |
| **GET**    | `/api/v1/permissions`            | List all permissions          | ✅             |
| **POST**   | `/api/v1/roles/{id}/permissions` | Assign permissions to role    | ✅ (admin)     |
| **GET**    | `/api/v1/me`                     | Get current user info & roles | ✅             |


🚀 Strategy Overview

We'll combine token-based authentication, tenant-context enforcement, and RBAC middleware:

```css
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
| timestamp | 2025-10-11T14:23:12Z      |


3. 🧩 Bonus: Advanced Hardening

Rotate signing keys (JWKS) regularly.

Deny access by default (zero-trust model).

Multi-tenant DB filters via ORM decorators.

JWT caching for performance (e.g., Redis token verifier).

Use OPA (Open Policy Agent) or Casbin if policies become complex.


### 🔐 1. Security & Access Control Enhancements
1.1. Row-Level Security (RLS) in PostgreSQL
1.2. Scoped JWT Claims
1.3. Token Introspection & Blacklisting
1.4. Encrypted at Rest + Transit

### 🧩 2. Architecture Enhancements
2.1. API Gateway Enforcement
2.2. Decouple Services via Events
2.3. Policy Engine (OPA / Casbin / Zanzibar)

### ⚙️ 3. Data Modeling & Schema Enhancements
3.1. Soft Deletes with “Deleted At”
3.2. Versioned Configs
3.3. Tenant “Type” Column
3.4. Multi-Tenant Metadata Indexing

### 🧠 4. Performance & Scalability
4.1. Read/Write Split
4.2. Caching Layer (Redis)
4.3. Query-level Auditing

### 📈 5. Observability, Governance, and Compliance
5.1. Structured Logging
5.2. Distributed Tracing
5.3. Data Governance


🧭 Summary: Modern Multi-Tenant RBAC Blueprint
| Area         | Enhancement                         | Benefit                        |
| ------------ | ----------------------------------- | ------------------------------ |
| Security     | RLS + Scoped JWT + Token revocation | Bulletproof isolation          |
| Architecture | API Gateway + Event Bus             | Scalability + clean boundaries |
| Data         | Versioned configs + soft deletes    | Auditability                   |
| Performance  | Redis caching + read replicas       | Low latency under scale        |
| Governance   | Structured logs + OpenTelemetry     | Observability + compliance     |
