# 🟩 IMA-Service — Task List

## 1. Project Setup
- [x] Scaffold FastAPI project
- [x] PostgreSQL config + session
- [] Structured JSON logging
- [x] Health check API
- [x] Alembic migrations
- [ ] Dockerfile + docker-compose
- [ ] CI/CD with lint/typecheck/tests

---

## 2. User Management
- [x] User model: id, email, hashed_password, is_active, is_superuser, timestamps
- [x] CRUD ops (`get_user_by_email`, `create_user`, etc.)
- [x] Unique constraints (email)
- [x] Account deactivation / deletion
- [ ] Email verification workflow 🚧
- [ ] Password reset workflow 🚧

---

## 3. Authentication (JWT)
- [x] Endpoints:
  - POST `/auth/login`
  - POST `/auth/refresh`
  - POST `/auth/logout`
- [x] Access + refresh tokens
  - `create_access_token`, `create_refresh_token`, `decode_token`
- [x] Token expiration (short-lived access, long-lived refresh)
- [ ] Rotate refresh tokens 🚧
- [ ] Blacklist revoked refresh tokens (Redis) 🚧
- [ ] JWT key rotation support 🚧

---

## 4. RBAC & Roles
- [x] **Database Models**
  - Role table (id, name, description, is_system)
- [x] **Default Roles**
  - `tenant_admin`, `member`, `billing_admin`, `viewer`
- [x] **Endpoints**
  - POST `/users/{id}/roles`
  - POST `/roles` (sys-admin only)
- [ ] **RBAC Enforcement**
  - `require_roles(...)` dependency
  - Roles embedded in JWT payload
  - Token scoped per tenant (claims: tenant_id + role)
- [ ] **Caching**
  - Cache `user → roles` lookup in Redis
  - Invalidate cache on role updates
- [ ] **Audit Logging**
  - Log role assignments (actor, target, role, tenant, timestamp)

---

📋 Execution Plan (file order)

✅ core/config.py → we finished.

➡️ utils/cache.py → caching abstraction.

utils/audit.py → audit logger.

api/deps.py → require_roles dependency + JWT decode.

crud/user.py → hook cache invalidation + audit log.

api/v1/routes/user.py → secure routes with RBAC.
🔑 Prep for Tenant-Service Integration

RBAC & Roles

- Add tenant_id to all role assignment APIs

- Update assign_role_to_user to require tenant_id

- Plan require_roles(...) dependency to check role + tenant

Authentication

- Embed tenant_id in JWT claims alongside roles

- Update token creation/decoding to support tenant_id

User ↔ Tenant linkage

- Create a Tenant-Service client stub (check_membership, list_tenants_for_user)

- Use stub now, replace with real Tenant-Service later

Caching

- Use tenant-scoped cache keys (roles:{user_id}:{tenant_id})

- Invalidate cache per (user_id, tenant_id) updates

Audit Logging

- Always log tenant_id in role changes and RBAC events

---

## 5. Integration with Tenant-Service
- [ ] Sync memberships from Tenant-Service
- [ ] Validate that `user_id + tenant_id` exists before granting roles
- [ ] Enforce tenant isolation when issuing tokens

---

## 6. Observability & Security
- [ ] Structured logs (auth, role changes, RBAC failures)
- [ ] Expose `/health` (DB, Redis)
- [ ] Prometheus metrics 🚧
- [ ] Tracing (OpenTelemetry) 🚧
- [ ] Secrets rotation (JWT keys, DB passwords)🚧


# 📂 project structure
```bash
ima_service/app
├── api
│   ├── __init__.py       # Makes api a package
│   ├── deps.py          # Shared FastAPI dependencies (DB session,auth etc.)
│   ├── v1
│   │   ├── __init__.py     # Marks v1 as a package
│   │   ├── api.py          # Collects and registers all v1 routes
│   │   └── routes
│   │       ├── __init__.py   # Marks routes folder as package
│   │       └── user.py      # v1 user-related API endpoints
│   ├── v2
│   │   ├── __init__.py     # Placeholder for next API version
│   │   ├── api.py         # Collects and registers v2 routes
│   │   └── routes
│   │       ├── __init__.py
│   │       └── user.py    # v2 user endpoints (future changes)
│
├── core
│   ├── __init__.py
│   └── config.py        # Settings and environment configuration
│
├── crud
│   ├── __init__.py
│   └── user.py          # DB access logic for users (CRUD functions)
│
├── db
│   ├── __init__.py
│   ├── base.py         # Import Base and models for Alembic autogeneration
│   ├── base_class.py   # SQLAlchemy declarative base
│   ├── init_db.py      # Initial DB seeding logic
│   └── session.py      # Engine and async session setup
│
├── models
│   ├── __init__.py
│   └── user.py         # SQLAlchemy User model definition
│
├── schemas
│   ├── __init__.py
│   └── user.py         # Pydantic schemas for request/responsevalidation
│
├── utils
│   ├── __init__.py
│   └── security.py    # Password hashing, verification, auth helpers
│
└── main.py            # FastAPI app entrypoint, includes routers

```