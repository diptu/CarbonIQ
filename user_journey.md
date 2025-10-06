# RBAC Sanity Test — Personas, Journeys, Seed Data & Multi-Tenancy Design

This document defines **RBAC personas**, their journeys, **role hierarchy**, and includes a **multi-tenancy/domain strategy** with example **seed data** for Apple, Orange, and Peanut tenants.

---

## 🔑 Role Hierarchy (Inheritance of Access)

* **TENANT_ADMIN** → inherits all functionality of `BILLING_ADMIN`, `MEMBER`, and `VIEWER`.
* **BILLING_ADMIN** → inherits all functionality of `MEMBER` and `VIEWER`.
* **MEMBER** → inherits all functionality of `VIEWER`.
* **VIEWER** → base read-only role.

---

## 👤 User Personas

### 🟩 Tenant Admin

* **Who:** Primary owner/manager of a tenant.
* **Responsibilities:** Invite, deactivate, and assign roles. Manage tenant/sub-tenant settings.
* **Access Scope:** Full tenant control (plan limits enforced).

### 🟧 Billing Admin

* **Who:** Finance/accounting staff.
* **Responsibilities:** Manage billing, invoices, and subscriptions.
* **Access Scope:** Billing + usage data, plus Member + Viewer permissions.

### 🟨 Member

* **Who:** Regular team members (engineers, analysts).
* **Responsibilities:** Create and edit tenant resources.
* **Access Scope:** CRUD on resources, plus Viewer permissions.

### 🟦 Viewer

* **Who:** Stakeholders (execs, auditors, consultants).
* **Responsibilities:** Read-only dashboards and reports.
* **Access Scope:** Read-only.

---

## 🧾 Subscription Plan Tiers

| Plan           | Max Active Users | Features                                                                 |
| -------------- | ---------------- | ------------------------------------------------------------------------ |
| **Basic**      | 1                | Limited features, file uploads only (small quota), **no Billing Admin**. |
| **Standard**   | 10               | Full RBAC support, all features enabled, access to integrations.         |
| **Enterprise** | 100              | Multi-vendor/sub-tenant support, compliance, unlimited uploads, SLAs.    |

---

## 🏢 Multi-Tenancy & Domain Strategy

### Domains

* Each **parent tenant** gets a **unique subdomain**:

  * Apple → `apple.carboniq.com`
  * Orange → `orange.carboniq.com`
  * Peanut → `peanut.carboniq.com`

* Each **sub-tenant** gets a **nested subdomain**:

  * Orchard Apple → `orchard.apple.carboniq.com`
  * Summit Apple → `summit.apple.carboniq.com`
  * Harbor Apple → `harbor.apple.carboniq.com`
  * Grove Orange → `grove.orange.carboniq.com`
  * Horizon Orange → `horizon.orange.carboniq.com`

### Schema Isolation

* **Each tenant (parent or sub-tenant) has its own schema** to ensure strict data isolation.
* **Parent tenants** have **read + write access to their sub-tenant schemas**.
* **Sub-tenants** can only access their **own schema** (no upward or cross-tenant access).
* **Cross-tenant access is always denied** (Apple cannot see Orange data, etc.).

### Tenant DB Model

```python
class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # Apple, Orange, Peanut
    domain = Column(String, unique=True, nullable=False)  # apple.carboniq.com
    schema_name = Column(String, unique=True, nullable=False)  # e.g. tenant_apple
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    parent = relationship("Tenant", remote_side=[id], backref="sub_tenants")
```

* **Parent Tenant:** `parent_id = NULL`, can query across own and sub-tenant schemas.
* **Sub-Tenant:** `parent_id = <parent_tenant_id>`, isolated schema, cannot access parent or sibling schemas.

---

## 🌱 Seed Data (Users & Tenants)

### 1. Apple Inc. (Enterprise — 100 users)

* **Domain:** `apple.carboniq.com`
* **Schema:** `tenant_apple`
* **Users:**

  * `admin@apple.com` → TENANT_ADMIN
* **Sub-Tenants:**

  * **Orchard Apple** (`orchard.apple.carboniq.com`, schema: `tenant_orchard_apple`)

    * `billing@orchard.apple.com` → BILLING_ADMIN
    * `member@orchard.apple.com` → MEMBER
    * `viewer@orchard.apple.com` → VIEWER
  * **Summit Apple** (`summit.apple.carboniq.com`, schema: `tenant_summit_apple`) → no seed users yet
  * **Harbor Apple** (`harbor.apple.carboniq.com`, schema: `tenant_harbor_apple`) → no seed users yet

### 2. Orange Ltd. (Standard — 10 users)

* **Domain:** `orange.carboniq.com`
* **Schema:** `tenant_orange`
* **Users:**

  * `admin@orange.com` → TENANT_ADMIN
* **Sub-Tenants:**

  * **Grove Orange** (`grove.orange.carboniq.com`, schema: `tenant_grove_orange`)

    * `member@grove.orange.com` → MEMBER
  * **Horizon Orange** (`horizon.orange.carboniq.com`, schema: `tenant_horizon_orange`)

    * `viewer@horizon.orange.com` → VIEWER

### 3. Peanut Corp. (Basic — 1 user)

* **Domain:** `peanut.carboniq.com`
* **Schema:** `tenant_peanut`
* **Users:**

  * `admin@peanut.com` → TENANT_ADMIN
* **Sub-Tenants:** none allowed on Basic plan.

```sql
-- 🌱 Seed Roles (if not already present)
INSERT INTO public.roles (id, name, description, is_system)
VALUES
    (gen_random_uuid(), 'TENANT_ADMIN', 'Tenant Administrator', true),
    (gen_random_uuid(), 'BILLING_ADMIN', 'Billing Administrator', true),
    (gen_random_uuid(), 'MEMBER', 'Regular Member', true),
    (gen_random_uuid(), 'VIEWER', 'Read-only User', true)
ON CONFLICT (name) DO NOTHING;

-- 🌱 Seed Tenants
WITH main_tenants AS (
    INSERT INTO public.tenants (id, name, domain, schema_name)
    VALUES
        (gen_random_uuid(), 'Apple Inc.', 'apple.carboniq.com', 'tenant_apple'),
        (gen_random_uuid(), 'Orange Ltd.', 'orange.carboniq.com', 'tenant_orange'),
        (gen_random_uuid(), 'Peanut Corp.', 'peanut.carboniq.com', 'tenant_peanut')
    ON CONFLICT (domain) DO NOTHING
    RETURNING id, name
),
apple_subs AS (
    INSERT INTO public.tenants (id, name, domain, schema_name, parent_id)
    SELECT gen_random_uuid(), 'Orchard Apple', 'orchard.apple.carboniq.com', 'tenant_orchard_apple', id
    FROM main_tenants WHERE name = 'Apple Inc.'
    UNION ALL
    SELECT gen_random_uuid(), 'Summit Apple', 'summit.apple.carboniq.com', 'tenant_summit_apple', id
    FROM main_tenants WHERE name = 'Apple Inc.'
    UNION ALL
    SELECT gen_random_uuid(), 'Harbor Apple', 'harbor.apple.carboniq.com', 'tenant_harbor_apple', id
    FROM main_tenants WHERE name = 'Apple Inc.'
    ON CONFLICT (domain) DO NOTHING
    RETURNING id, name
),
orange_subs AS (
    INSERT INTO public.tenants (id, name, domain, schema_name, parent_id)
    SELECT gen_random_uuid(), 'Grove Orange', 'grove.orange.carboniq.com', 'tenant_grove_orange', id
    FROM main_tenants WHERE name = 'Orange Ltd.'
    UNION ALL
    SELECT gen_random_uuid(), 'Horizon Orange', 'horizon.orange.carboniq.com', 'tenant_horizon_orange', id
    FROM main_tenants WHERE name = 'Orange Ltd.'
    ON CONFLICT (domain) DO NOTHING
    RETURNING id, name
)
SELECT 1;

-- 🌱 Seed Users
WITH inserted_users AS (
    INSERT INTO public.users (id, email, hashed_password, is_active, is_superuser)
    VALUES
        (gen_random_uuid(), 'admin@apple.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'billing@orchard.apple.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'member@orchard.apple.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'viewer@orchard.apple.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'admin@orange.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'member@grove.orange.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'viewer@horizon.orange.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false),
        (gen_random_uuid(), 'admin@peanut.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C', true, false)
    ON CONFLICT (email) DO NOTHING
    RETURNING id, email
)
SELECT 1;

-- 🌱 Assign Roles
INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Apple Inc.'
WHERE u.email = 'admin@apple.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'BILLING_ADMIN'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'billing@orchard.apple.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'MEMBER'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'member@orchard.apple.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'VIEWER'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'viewer@orchard.apple.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Orange Ltd.'
WHERE u.email = 'admin@orange.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'MEMBER'
JOIN public.tenants t ON t.name = 'Grove Orange'
WHERE u.email = 'member@grove.orange.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'VIEWER'
JOIN public.tenants t ON t.name = 'Horizon Orange'
WHERE u.email = 'viewer@horizon.orange.com'
UNION ALL
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Peanut Corp.'
WHERE u.email = 'admin@peanut.com';

```

## Pytest Test Plan for Multi-Tenant RBAC
1. Role Inheritance Hierarchy

test_tenant_admin_can_do_billing_admin_tasks

test_tenant_admin_can_do_member_tasks

test_tenant_admin_can_do_viewer_tasks

test_billing_admin_can_do_member_tasks

test_billing_admin_can_do_viewer_tasks

test_member_can_do_viewer_tasks

test_viewer_cannot_do_member_tasks

test_member_cannot_do_billing_tasks

test_billing_admin_cannot_do_tenant_admin_tasks

2. Tenant Admin Tests

test_tenant_admin_can_manage_parent_tenant

test_tenant_admin_can_manage_subtenants

test_tenant_admin_cannot_access_other_tenants

test_tenant_admin_can_assign_roles_in_subtenants

test_tenant_admin_inherits_billing_permissions

test_tenant_admin_inherits_member_permissions

test_tenant_admin_inherits_viewer_permissions

3. Billing Admin Tests

test_billing_admin_can_manage_billing

test_billing_admin_cannot_manage_roles

test_billing_admin_cannot_create_subtenants

test_billing_admin_cannot_manage_parent_or_sibling_tenants

test_billing_admin_inherits_member_permissions

test_billing_admin_inherits_viewer_permissions

4. Member Tests

test_member_can_access_basic_features

test_member_cannot_manage_roles_or_billing

test_member_cannot_create_subtenants

test_member_inherits_viewer_permissions

5. Viewer Tests

test_viewer_can_read_data_only

test_viewer_cannot_create_update_delete

test_viewer_cannot_manage_roles

test_viewer_cannot_manage_billing

6. Cross-Tenant Isolation

test_parent_admin_cannot_access_other_tenant

test_subtenant_admin_cannot_manage_parent

test_subtenant_admin_cannot_manage_sibling_tenants

test_cross_tenant_admin_isolation

7. Plan Enforcement

test_basic_plan_cannot_have_subtenants

test_standard_plan_limited_subtenants

test_enterprise_plan_multiple_subtenants

8. Security & Constraints

test_duplicate_role_assignment_not_allowed

test_user_cannot_promote_self

test_conflicting_roles_handled_correctly

test_disabled_user_cannot_login

✅ Role-Based Access Control (RBAC) with Explicit Permission Inheritance
1. Store Roles & Permissions in DB

Roles Table (id, name, level, description)

Permissions Table (id, name, description)

Role_Permissions Table (many-to-many: role_id ↔ permission_id)

User_Roles Table (user_id, tenant_id, role_id)

This gives flexibility: you can add roles/permissions without code changes.

```sql
-- Create tenants table with parent_id
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    schema_name VARCHAR(255) UNIQUE NOT NULL,
    parent_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO tenants (id, name, domain, schema_name, parent_id)
VALUES (gen_random_uuid(), 'demo', 'demo.carboniq.com', 'tenant_carboniq', NULL);
```