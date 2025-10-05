# IMA Service - DB-driven RBAC & Tenant-aware Architecture

This document describes the best practices and design guidelines for implementing **DB-driven Role-Based Access Control (RBAC)** in the IMA Service, supporting **roles, permissions, hierarchical access, and multi-tenant awareness**.

---

## 1️⃣ Database Design

**Tables:**

### **roles**

* `id` (UUID, PK)
* `name` (Enum/str, unique per system)
* `level` (int, hierarchy level; higher = more privileges)
* `description` (optional)
* `is_system` (bool, true for system-defined roles)

### **permissions**

* `id` (UUID, PK)
* `name` (str, unique)
* `description` (optional)

### **role_permissions** (many-to-many)

* `role_id` → `roles.id`
* `permission_id` → `permissions.id`
* Composite PK (`role_id`, `permission_id`)

### **users**

* `id` (UUID, PK)
* `email` (str, unique)
* `hashed_password` (str)
* `is_active` (bool)
* `is_superuser` (bool, internal only)
* `tenant_id` → `tenants.id`

### **user_roles** (many-to-many, per tenant)

* `user_id` → `users.id`
* `role_id` → `roles.id`
* `tenant_id` → `tenants.id`
* Composite PK (`user_id`, `role_id`, `tenant_id`)
* Enforce **one role per user per tenant** if desired.

### **tenants**

* `id` (UUID, PK)
* `name` (str, unique)
* `domain` (str, unique)
* `schema_name` (str, optional; useful for multi-schema deployments)
* `parent_id` → `tenants.id` (nullable)

---

## 2️⃣ Role Hierarchy

* **Use `level` field** for hierarchical permissions:

  * `VIEWER` → `MEMBER` → `BILLING_ADMIN` → `TENANT_ADMIN`
* Higher-level roles **inherit permissions of lower-level roles**.
* Enforce hierarchy in **role assignment & permission checks**.

---

## 3️⃣ Tenant Awareness

* Every user **belongs to a tenant** (`tenant_id`).
* Role assignments are **tenant-scoped**.
* JWT tokens include:

  ```json
  {
    "user_id": "...",
    "tenant_id": "...",
    "roles": ["VIEWER"]
  }
  ```
* Service logic always checks **tenant_id** in queries.

---

## 4️⃣ Permissions

* Permissions are **action-specific** (e.g., `manage_billing`, `view_reports`).
* Assign permissions to roles via `role_permissions`.
* Check permissions in endpoints:

  ```python
  def check_permission(user, permission_name, tenant_id):
      roles = db.query(UserRole).filter(
          UserRole.user_id == user.id,
          UserRole.tenant_id == tenant_id
      ).all()
      for role in roles:
          if permission_name in [p.name for p in role.permissions]:
              return True
      return False
  ```

---

## 5️⃣ API / Service Guidelines

1. **Endpoints return roles & permissions**:

   * `GET /users/{id}` → `roles` with `permissions`
   * `GET /roles` → `permissions`

2. **Role assignment logic:**

   * Assign default role (`VIEWER`) if none provided.
   * Prevent assigning roles higher than allowed by tenant admin.

3. **JWT token includes:**

   * `user_id`, `tenant_id`, `roles`
   * Avoid including permissions to reduce payload; compute dynamically.

4. **Service-layer permission checks:**

   * Always check `tenant_id` scope
   * Use `role.level` for hierarchical access

5. **Superuser logic:**

   * `is_superuser=True` users bypass RBAC checks
   * Only internal system users can set this flag

---

## 6️⃣ Code Best Practices

* **Schemas**:

  * Pydantic with type hints and docstrings
  * `UserRead` includes roles and permissions
* **Models**:

  * SQLAlchemy with `Base` & `TimestampMixin`
  * Association tables for `user_roles` and `role_permissions`
* **Migrations**:

  * Use Alembic; seed system roles and permissions
* **Multi-tenant**:

  * Include `tenant_id` in user-role and JWT payload
  * Queries always filter by `tenant_id`

---

## 7️⃣ Security Considerations

* Never allow client to assign `is_superuser`
* Validate all tenant-scoped queries
* Hash passwords (e.g., bcrypt)
* Limit JWT lifetime; refresh token securely
* Audit all RBAC-sensitive actions

---

## 8️⃣ Default Role Assignment

* **New users** are automatically assigned `VIEWER` if no roles are provided.
* Ensures minimum access and prevents privilege escalation.
