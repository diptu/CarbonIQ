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
