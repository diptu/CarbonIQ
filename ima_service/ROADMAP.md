# IMA Service – Full Task List

## ✅ 1. Project Setup
- [x] Scaffold FastAPI project
- [x] Configure PostgreSQL
- [x] Setup .env for configs
- [x] Create database session (AsyncSession)
- [] Configure Alembic for migrations
- [x] Configure logging and structured logs (JSON) for observability  ⏳
- []  Performance bench mark with locust. 🚧
- [] Include Sentry / error reporting integration (optional but recommended)  🚧
- [x] Set up UV as package manager and lock dependencies (`uv.lock`)
- [x] Configure pre-commit hooks: ruff, black, isort, mypy, pylint
- [x] Health check api

---

## ✅ 2. Core Auth & Users
- [] User model (`User`)
- [] Fields: id, email, hashed_password, role, is_active, is_superuser,
      created_at, updated_at
- [] CRUD operations (`get_user_by_email`, `create_user`, etc.)
- [] Email verification flow for new users as a background task 🚧
- [] Password reset workflow (token + email) as a background task🚧
- [] Unique constraints on email and username
- [] Pydantic schemas (`UserCreate`, `UserLogin`, etc.)
- [] Account deactivation / deletion endpoints  🚧

---

## ✅ 3. JWT Authentication
- [] Implement access + refresh tokens
- [] `create_access_token`, `create_refresh_token`, `decode_token`
- [] Login endpoint issues both tokens
- [] Refresh endpoint issues new access token
- [] Token expiration handling (access short-lived, refresh long-lived)
- [] Rotate refresh tokens on usage for better security 🚧
- [] Blacklist expired/revoked refresh tokens (Redis recommended)🚧
- [] JWT key rotation support for long-term security  🚧

---

## ✅ 4. RBAC / Roles
- [] Enum for `UserRole` (USER, ADMIN)
  - [] Consider hierarchical roles (USER < MODERATOR < ADMIN)
- [] Include role in JWT payload
- [] `require_roles` dependency for endpoint protection
  - [] Add endpoint decorators for role checks
- [] Admin-only and user-or-admin endpoints
- [] Unit tests for role enforcement  🚧

---

## ⏳ 5. Social Login / OAuth 2.0
- [] Integrate providers: Google, Facebook, GitHub, Apple
- [] Handle OAuth flow:
  - [] Verify provider tokens on server side
  - [] Frontend redirects to provider login
  - [] Provider returns authorization code / token
  - [] Exchange code for user info
- [] Auto-create new user if first-time login
- [] Issue standard JWT access + refresh tokens
- [] Include role in JWT payload
- [] Optional: Link multiple social accounts to the same user  🚧
  - [] Store provider IDs and link multiple accounts to same user
- [] Add rate limiting for login attempts to prevent abuse
- [] Optional: Profile picture / basic info sync from provider

---

## ✅ 6. Tests & Quality
- [] Unit & integration tests
- [] JWT flows, refresh tokens, role enforcement
- [] pytest for async endpoints
- [] mypy type checking
- [] pylint linting
- [] Code documentation
- [] End-to-end tests (simulate OAuth and token refresh)
- [] Load tests / stress tests for 200M users scale  🚧
- [] Database migration tests with Alembic  🚧
- [x] CI/CD workflow (GitHub Actions or GitLab) to run lint, typecheck, tests

---

## ⏳ 7. Remaining Enhancements
- [] Refresh token revocation / blacklist (Redis or DB-backed)
- [] Rate limiting / brute-force prevention (Redis recommended)
- [] Detailed OpenAPI documentation with ResponseModel examples
- [] CI/CD linting & test automation
  - [] Dockerize tests from inside `infra/` directory 🚧
- [] Dockerize the service from inside `infra/` directory
- [] Build container image
- [] Configure environment variables (DB, JWT, Redis)
- [] Kubernetes deployment manifests  🚧
  - [] Deployment, Service, ConfigMap, Secret  🚧
  - [] Include Redis as sidecar or external service 🚧
- [] Health endpoints for DB, Redis, external services (using ResponseModel)
- [] Metrics / Prometheus integration for monitoring  🚧
- [] Tracing (OpenTelemetry) for distributed requests  🚧
- [] Secrets management (Vault or K8s Secrets) for sensitive data
- [] Horizontal scaling considerations: sticky sessions, load balancer  🚧
- [] Caching layer (Redis or in-memory) for frequently requested data
- [] API versioning (`/v1`, `/v2`)  🚧
- [] Graceful startup / shutdown events for FastAPI  🚧
