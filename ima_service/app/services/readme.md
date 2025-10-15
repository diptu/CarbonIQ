# 📋 Service Layer Implementation Checklist (100% Readiness)

1. base_service.py 🏠 (The Security Foundation)
   🔒 Define an Abstract BaseService class.
   🔒 Implement a Context Retrieval Property for current_user_id and tenant_id from the request context.
   🔒 Implement scope_query(query) to automatically and mandatorily apply the current tenant_id filter to all queries.
   🔒 Define a robust @transactional decorator to guarantee data atomicity and rollback on exceptions.

2. auth_service.py 🔑 (Authentication & Token Security)
   🔒 Implement login() with password complexity checks and failed login attempt tracking.
   🔒 Implement issue_tokens() ensuring the payload includes sub, tenant_id, and all effective permissions.
   🔒 Implement revoke_token(jti): DB revocation AND instant JTI writing to Redis blacklist.
   🔒 Implement high-speed check_token_blacklist(jti) against the Redis cache for token validation.
   🌟 Implement the full MFA setup/verification flow.

3. user_service.py 👤 (User Management)
   🔒 Scoped CRUD: All operations must use scope_query.
   🔒 RBAC Pre-Check: All CRUD methods must call rbac_service.check_access() first.
   🔒 Implement deactivate_user() to cascadingly soft−delete the User AND explicitly revoke all associated AuthTokens.
   🔒 Implement invite_user flow to manage PENDING status and secure InvitationToken handling.

4. role_service.py / permission_service.py 👑 (RBAC Definitions)
   🔒 Implement a pre-commit check to reject any UPDATE or DELETE on roles where is_system_role = TRUE.
   🔒 Implement get_effective_permissions(role_id) with caching to aggregate inherited permissions.
   🔒 Implement atomic link_permission and unlink_permission methods.
   🌟 Implement logic for effective_from/to fields during role updates for historical auditing.

5. rbac_service.py 🚦 (The Gatekeeper)
   🔒 Implement the final, definitive check_access(user_id,permission_code,tenant_id) method.
   🌟 Define a clear interface for Policy Hook integration.

6. audit_adapter.py 📝 (Audit Logging)
   🔒 Implement the log_action() standardized interface.
   🔒 Implement logic to automatically retrieve and inject the user_id, tenant_id, trace_id, and correlation_id from the execution context.

7. Domain Services (e.g., billing_service.py) 💡
   🔒 Strict RBAC Enforcement: Every method exposed must begin by calling rbac_service.check_access().
   🔒 Strict Tenant Scoping: Every database query must use the scope_query method.
   🔒 Implement try/except/finally logic to ensure audit_adapter.log_action is called after a successful commit AND upon catching an exception.


# Implementaion order 
## v1.1:

```css
+------------------------+
|      Minimal IMA Service       |
|  (Authentication & RBAC)       |
+------------------------+
| Endpoints (minimal subset):   |
| 1. Auth APIs                  |
|    - POST /auth/login         |
|    - POST /auth/refresh       |
| 2. User APIs                  |
|    - GET /users/{id}          |
|    - POST /users              |
| 3. Roles & Permissions APIs   |
|    - GET /roles/{id}          |
|    - POST /roles              |
|    - POST /roles/{id}/permissions |
+------------------------+
           |
           | JWTs (RS256 signed) + tenant_id + roles + permissions
           v
+------------------------+
|   Gateway Service       |
+------------------------+
| Responsibilities:      |
| - JWT validation middleware (RS256) |
| - Tenant scoping middleware        |
| - RBAC enforcement middleware      |
| - Routing to microservices        |
| - Audit logging / observability   |
| - Optional BFF endpoints          |
+------------------------+
           |
           | Validated request with tenant context & RBAC enforced
           v
+------------------------+
|  Tenant Service        |
+------------------------+
| Endpoints:             |
| - POST /tenants        |
| - GET /tenants         |
| - GET /tenants/{id}    |
| - PUT /tenants/{id}    |
| - DELETE /tenants/{id} |
| - POST /tenants/{id}/memberships |
| Notes: Requires JWT from Minimal IMA |
| Tenant context injected via Gateway |
| RBAC check enforced via Gateway |
+------------------------+
           |
           | Tenant-aware, RBAC-secured calls
           v
+------------------------+
| Downstream Services    |
| (Billing, Reporting,   |
|  OCR, AI, Factor, etc.)|
+------------------------+
| Responsibilities:      |
| - Enforce tenant_id from request |
| - Enforce RBAC if needed         |
| - Audit all sensitive actions    |
| - Operate without direct auth logic (relies on Gateway) |
+------------------------+

```

## v1.2:

```css

+------------------------+
|      IMA Service       |
|  (Authentication & RBAC)  |
+------------------------+
| Endpoints:             |
| 1. Auth APIs           |
|    - POST /auth/login         |
|    - POST /auth/refresh       |
|    - POST /auth/logout        |
| 2. User APIs             |
|    - GET /users               |
|    - GET /users/{id}          |
|    - POST /users              |
|    - PUT /users/{id}          |
|    - POST /users/invite       |
|    - POST /users/{id}/deactivate |
| 3. Roles & Permissions APIs   |
|    - GET /roles               |
|    - GET /roles/{id}          |
|    - POST /roles              |
|    - PUT /roles/{id}          |
|    - DELETE /roles/{id}       |
|    - POST /roles/{id}/permissions        |
|    - DELETE /roles/{id}/permissions/{permission_id} |
|    - GET /permissions         |
| 4. Audit Logging (internal)   |
+------------------------+
           |
           | JWTs (RS256 signed) + tenant_id + roles + permissions
           v
+------------------------+
|   Gateway Service       |
+------------------------+
| Responsibilities:      |
| - JWT validation middleware (RS256) |
| - Tenant scoping middleware        |
| - RBAC enforcement middleware      |
| - Routing to microservices        |
| - Audit logging / observability   |
| - Optional BFF endpoints          |
+------------------------+
           |
           | Validated request with tenant context & RBAC enforced
           v
+------------------------+
|  Tenant Service        |
+------------------------+
| Endpoints:             |
| - POST /tenants        |
| - GET /tenants         |
| - GET /tenants/{id}    |
| - PUT /tenants/{id}    |
| - DELETE /tenants/{id} |
| - POST /tenants/{id}/memberships |
| Notes: Requires JWT from IMA |
| Tenant context injected via Gateway |
| RBAC check enforced via Gateway |
+------------------------+
           |
           | Tenant-aware, RBAC-secured calls
           v
+------------------------+
| Downstream Services    |
| (Billing, Reporting,   |
|  OCR, AI, Factor, etc.)|
+------------------------+
| Responsibilities:      |
| - Enforce tenant_id from request |
| - Enforce RBAC if needed         |
| - Audit all sensitive actions    |
| - Operate without needing direct auth logic (relies on Gateway) |
+------------------------+

```

Flow Summary:

User authenticates via IMA Service → receives JWT with tenant_id, roles, permissions.

Client sends request to Gateway Service → JWT validated, RBAC enforced, tenant context injected.

Gateway routes request to Tenant Service or other downstream services.

Tenant Service performs business logic → tenant-aware & RBAC-secured.

Downstream services operate using tenant context → all actions logged to audit.