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

  * Apple → `apple.saas.com`
  * Orange → `orange.saas.com`
  * Peanut → `peanut.saas.com`

* Each **sub-tenant** gets a **nested subdomain**:

  * Orchard Apple → `orchard.apple.saas.com`
  * Summit Apple → `summit.apple.saas.com`
  * Harbor Apple → `harbor.apple.saas.com`
  * Grove Orange → `grove.orange.saas.com`
  * Horizon Orange → `horizon.orange.saas.com`

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
    domain = Column(String, unique=True, nullable=False)  # apple.saas.com
    schema_name = Column(String, unique=True, nullable=False)  # e.g. tenant_apple
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    parent = relationship("Tenant", remote_side=[id], backref="sub_tenants")
```

* **Parent Tenant:** `parent_id = NULL`, can query across own and sub-tenant schemas.
* **Sub-Tenant:** `parent_id = <parent_tenant_id>`, isolated schema, cannot access parent or sibling schemas.

---

## 🌱 Seed Data (Users & Tenants)

### 1. Apple Inc. (Enterprise — 100 users)

* **Domain:** `apple.saas.com`
* **Schema:** `tenant_apple`
* **Users:**

  * `admin@apple.com` → TENANT_ADMIN
* **Sub-Tenants:**

  * **Orchard Apple** (`orchard.apple.saas.com`, schema: `tenant_orchard_apple`)

    * `billing@orchard.apple.com` → BILLING_ADMIN
    * `member@orchard.apple.com` → MEMBER
    * `viewer@orchard.apple.com` → VIEWER
  * **Summit Apple** (`summit.apple.saas.com`, schema: `tenant_summit_apple`) → no seed users yet
  * **Harbor Apple** (`harbor.apple.saas.com`, schema: `tenant_harbor_apple`) → no seed users yet

### 2. Orange Ltd. (Standard — 10 users)

* **Domain:** `orange.saas.com`
* **Schema:** `tenant_orange`
* **Users:**

  * `admin@orange.com` → TENANT_ADMIN
* **Sub-Tenants:**

  * **Grove Orange** (`grove.orange.saas.com`, schema: `tenant_grove_orange`)

    * `member@grove.orange.com` → MEMBER
  * **Horizon Orange** (`horizon.orange.saas.com`, schema: `tenant_horizon_orange`)

    * `viewer@horizon.orange.com` → VIEWER

### 3. Peanut Corp. (Basic — 1 user)

* **Domain:** `peanut.saas.com`
* **Schema:** `tenant_peanut`
* **Users:**

  * `admin@peanut.com` → TENANT_ADMIN
* **Sub-Tenants:** none allowed on Basic plan.
