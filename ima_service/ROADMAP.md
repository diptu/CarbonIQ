# 🟩 IMA-Service — Task List

## 1. Project Setup
- [x] Scaffold FastAPI project
- [x] PostgreSQL config + session
- [] Structured JSON logging
- [] Health check API
- [ ] Alembic migrations
- [ ] Dockerfile + docker-compose
- [ ] CI/CD with lint/typecheck/tests

---

## 2. User Management
- [x] User model: id, email, hashed_password, is_active, is_superuser, timestamps
- [x] CRUD ops (`get_user_by_email`, `create_user`, etc.)
- [x] Unique constraints (email)
- [ ] Account deactivation / deletion
- [ ] Email verification workflow 🚧
- [ ] Password reset workflow 🚧

---

## 3. Authentication (JWT)
- [ ] Endpoints:
  - POST `/auth/login`
  - POST `/auth/refresh`
  - POST `/auth/logout`
- [ ] Access + refresh tokens
  - `create_access_token`, `create_refresh_token`, `decode_token`
- [ ] Token expiration (short-lived access, long-lived refresh)
- [ ] Rotate refresh tokens 🚧
- [ ] Blacklist revoked refresh tokens (Redis) 🚧
- [ ] JWT key rotation support 🚧

---

## 4. RBAC & Roles
- [ ] **Database Models**
  - Role table (id, name, description, is_system)
- [ ] **Default Roles**
  - `tenant_admin`, `member`, `billing_admin`, `viewer`
- [ ] **Endpoints**
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