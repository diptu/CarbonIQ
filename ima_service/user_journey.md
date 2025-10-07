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

---------------------------------------------------------------------------
-- 🌱 Seed Tenants
---------------------------------------------------------------------------
-- 🌱 Seed Tenants
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


-- 🌱 Seed  Apple Inc.
INSERT INTO tenants (id, name, domain, schema_name, parent_id)
VALUES
  (gen_random_uuid(), 'Apple Inc.', 'apple.carboniq.com', 'tenant_apple', NULL),
  (gen_random_uuid(), 'Orchard Apple', 'orchard.apple.carboniq.com', 'tenant_orchard_apple',
     (SELECT id FROM tenants WHERE name = 'Apple Inc.')),
  (gen_random_uuid(), 'Summit Apple', 'summit.apple.carboniq.com', 'tenant_summit_apple',
     (SELECT id FROM tenants WHERE name = 'Apple Inc.')),
  (gen_random_uuid(), 'Harbor Apple', 'harbor.apple.carboniq.com', 'tenant_harbor_apple',
     (SELECT id FROM tenants WHERE name = 'Apple Inc.'))
ON CONFLICT (domain) Do NOTHING

-- 🌱 Seed  Orange Ltd.
INSERT INTO tenants (id, name, domain, schema_name, parent_id)
VALUES
  (gen_random_uuid(), 'Grove Orange', 'grove.orange.carboniq.com', 'tenant_grove_orange',
     (SELECT id FROM main_tenants WHERE name = 'Orange Ltd.')),
  (gen_random_uuid(), 'Horizon Orange', 'horizon.orange.carboniq.com', 'tenant_horizon_orange',
     (SELECT id FROM main_tenants WHERE name = 'Orange Ltd.'))
ON CONFLICT (domain) DO NOTHING;

INSERT INTO tenants (id, name, domain, schema_name, parent_id)
VALUES
  (gen_random_uuid(), 'Orange Ltd.', 'orange.carboniq.com', 'tenant_orange', NULL),
  (gen_random_uuid(), 'Grove Orange', 'grove.orange.carboniq.com', 'tenant_grove_orange',
     (SELECT id FROM tenants WHERE name = 'Orange Ltd.')),
  (gen_random_uuid(), 'Horizon Orange', 'horizon.orange.carboniq.com', 'tenant_horizon_orange',
     (SELECT id FROM tenants WHERE name = 'Orange Ltd.'))
ON CONFLICT (domain) do nothing

-- 🌱 Seed  Peanut Corp.
INSERT INTO tenants (id, name, domain, schema_name, parent_id)
VALUES
  (gen_random_uuid(), 'Peanut Corp.', 'peanut.carboniq.com', 'tenant_peanut', NULL)
ON CONFLICT (domain) DO NOTHING;



--------------------------------------------------------------------------- 🌱 Seed Users
---------------------------------------------------------------------------
 -- 🍏 Apple Inc. - Enterprise

INSERT INTO users (id, email, hashed_password, tenant_id, is_active, is_superuser)
VALUES
  (gen_random_uuid(), 'admin@apple.com', '$2b$12$Or7b854QYKvRrnvBQORntO2.3jgMvHpdjngpozIHbtrDcukKraT3C',
     (SELECT id FROM tenants WHERE name='Apple Inc.'), TRUE, TRUE),
  (gen_random_uuid(), 'billing@orchard.apple.com', '$2b$12$ExampleHashedPassBilling',
     (SELECT id FROM tenants WHERE name='Orchard Apple'), TRUE, FALSE),
  (gen_random_uuid(), 'member@orchard.apple.com', '$2b$12$ExampleHashedPassMember',
     (SELECT id FROM tenants WHERE name='Orchard Apple'), TRUE, FALSE),
  (gen_random_uuid(), 'viewer@orchard.apple.com', '$2b$12$ExampleHashedPassViewer',
     (SELECT id FROM tenants WHERE name='Orchard Apple'), TRUE, FALSE)
ON CONFLICT (email) DO NOTHING

-- 🍊 Orange Ltd. - Standard
INSERT INTO users (id, email, hashed_password, tenant_id, is_active, is_superuser)
VALUES
  (gen_random_uuid(), 'admin@orange.com', '$2b$12$ExampleHashedPassAdminOrange',
     (SELECT id FROM tenants WHERE name='Orange Ltd.'), TRUE, TRUE),
  (gen_random_uuid(), 'member@grove.orange.com', '$2b$12$ExampleHashedPassMemberGrove',
     (SELECT id FROM tenants WHERE name='Grove Orange'), TRUE, FALSE),
  (gen_random_uuid(), 'viewer@horizon.orange.com', '$2b$12$ExampleHashedPassViewerHorizon',
     (SELECT id FROM tenants WHERE name='Horizon Orange'), TRUE, FALSE)
ON CONFLICT (email) DO NOTHING;

--------------------------------------------------------------------------- 🌱 Seed Roles
---------------------------------------------------------------------------

-- 🌱 Seed Roles (if not already present)
INSERT INTO public.roles (id, name, description, is_system)
VALUES
    (gen_random_uuid(), 'TENANT_ADMIN', 'Tenant Administrator', true),
    (gen_random_uuid(), 'BILLING_ADMIN', 'Billing Administrator', true),
    (gen_random_uuid(), 'MEMBER', 'Regular Member', true),
    (gen_random_uuid(), 'VIEWER', 'Read-only User', true)
ON CONFLICT (name) DO NOTHING;

-------


---------------------------------------------------------------------------
-- 🌱 Assign Roles to Users
---------------------------------------------------------------------------

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Apple Inc.'
WHERE u.email = 'admin@apple.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'BILLING_ADMIN'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'billing@orchard.apple.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'MEMBER'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'member@orchard.apple.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'VIEWER'
JOIN public.tenants t ON t.name = 'Orchard Apple'
WHERE u.email = 'viewer@orchard.apple.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Orange Ltd.'
WHERE u.email = 'admin@orange.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'MEMBER'
JOIN public.tenants t ON t.name = 'Grove Orange'
WHERE u.email = 'member@grove.orange.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'VIEWER'
JOIN public.tenants t ON t.name = 'Horizon Orange'
WHERE u.email = 'viewer@horizon.orange.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

INSERT INTO public.user_roles (user_id, role_id, tenant_id)
SELECT u.id, r.id, t.id
FROM public.users u
JOIN public.roles r ON r.name = 'TENANT_ADMIN'
JOIN public.tenants t ON t.name = 'Peanut Corp.'
WHERE u.email = 'admin@peanut.com'
ON CONFLICT (user_id, role_id, tenant_id) DO NOTHING;

```

## Test Plan for Multi-Tenant RBAC
| #  | Test Case                                  | User                        | Tenant          | Expected Result                          | Description / Purpose                                                                |
| -- | ------------------------------------------ | --------------------------- | --------------- | ---------------------------------------- | ------------------------------------------------------------------------------------ |
| 1  | Login as admin                             | `admin@apple.com`           | `Apple Inc.`    | Success                                  | Verify that admin can log in.                                                        |
| 2  | Login as billing user                      | `billing@orchard.apple.com` | `Orchard Apple` | Success                                  | Verify that billing user can log in.                                                 |
| 3  | Login as admin in other tenant             | `admin@orange.com`          | `Grove Orange`  | Success                                  | Verify that admin can log in to their own tenant.                                    |
| 4  | Login as basic-plan admin                  | `admin@peanut.com`          | `Peanut Corp.`  | Success                                  | Verify login for basic-plan admin.                                                   |
| 5  | Login as non-existent tenant admin         | `admin@peanut.com`          | Non-existent    | Success                                  | Verify login for admin assigned to non-existent tenant.                              |
| 6  | List users in own tenant                   | `billing@orchard.apple.com` | `Orchard Apple` | List only Orchard Apple users            | Validate that a tenant user can view users only within their own tenant.             |
| 7  | List users in parent/unrelated tenant      | `billing@orchard.apple.com` | `Apple Inc.`    | Fail: 403                                | Ensure that a tenant user cannot fetch users from parent or unrelated tenants.       |
| 8  | Create user in own tenant                  | `admin@apple.com`           | `Apple Inc.`    | Success                                  | Verify that an admin can create users within their own tenant.                       |
| 9  | Create user in child tenant                | `admin@apple.com`           | `Orchard Apple` | Success                                  | Ensure that parent-tenant admins can create users in child/sub-tenants.              |
| 10 | Create user in unrelated tenant            | `admin@apple.com`           | `Orange Ltd.`   | Fail: 403                                | Confirm that an admin cannot create users in tenants they do not belong to.          |
| 11 | Duplicate role assignment                  | Already existing user-role  | —               | Fail gracefully (IntegrityError handled) | Check that duplicate roles are handled gracefully without breaking the system.       |
| 12 | Create user in non-child tenant            | `admin@orange.com`          | `Grove Orange`  | Success                                  | Verify user creation for admins in their own tenant that has no sub-tenants.         |
| 13 | Create user under Basic plan tenant        | `admin@peanut.com`          | `Peanut Corp.`  | Success                                  | Test user creation for a basic-plan tenant to ensure standard permissions work.      |
| 14 | Create user under sub-tenant of Basic plan | `admin@peanut.com`          | Non-existent    | Fail: 403                                | Confirm that admins cannot create users in tenants that do not exist or are invalid. |


| #  | Test Case                      | User                                 | Tenant          | Expected Result                                              |
| -- | ------------------------------ | ------------------------------------ | --------------- | ------------------------------------------------------------ |
| 10 | List users in own tenant       | `billing@orchard.apple.com`          | `Orchard Apple` | Only Orchard Apple users                                     |
| 11 | List users in parent tenant    | `billing@orchard.apple.com`          | `Apple Inc.`    | Fail: 403                                                    |
| 12 | List users in unrelated tenant | `billing@orchard.apple.com`          | `Orange Ltd.`   | Fail: 403                                                    |
| 13 | Check role assignment          | Newly created user in allowed tenant | —               | Role assigned according to default policy (VIEWER ) |

| #  | Test Case                        | User                        | Tenant          | Expected Role                | Expected Result                             |
| -- | -------------------------------- | --------------------------- | --------------- | ---------------------------- | ------------------------------------------- |
| 14 | Create user under allowed tenant | `billing@orchard.apple.com` | `Orchard Apple` | VIEWER                       | User is created and role assigned correctly |
| 15 | Create user under parent tenant  | `billing@orchard.apple.com` | `Apple Inc.`    | N/A                          | Should fail: 403                            |
| 16 | Verify role mapping              | Newly created users         | Tenant          | Default role (VIEWER/MEMBER) | Role exists in `user_roles` table           |
