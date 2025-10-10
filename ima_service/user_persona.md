# RBAC Personas — Role Hierarchy, Multi-Tenancy & Seed Data

This file defines **RBAC personas**, their responsibilities, 
**role hierarchy**, and a **multi-tenancy/domain strategy** 
with example **seed data**.

---

## 🔑 Role Hierarchy (Inheritance)

* **TENANT_ADMIN** → inherits `BILLING_ADMIN`, `MEMBER`, `VIEWER`
* **BILLING_ADMIN** → inherits `MEMBER`, `VIEWER`
* **MEMBER** → inherits `VIEWER`
* **VIEWER** → base read-only role

---

## 👤 User Personas

### 🟩 Tenant Admin
* **Who:** Primary owner/manager of a tenant
* **Responsibilities:** Invite, deactivate, assign roles; manage tenant/sub-tenant settings
* **Access Scope:** Full tenant control (plan limits enforced)

### 🟧 Billing Admin
* **Who:** Finance/accounting staff
* **Responsibilities:** Manage billing, invoices, subscriptions
* **Access Scope:** Billing + usage data, plus Member + Viewer permissions

### 🟨 Member
* **Who:** Regular team members (engineers, analysts)
* **Responsibilities:** Create and edit tenant resources
* **Access Scope:** CRUD on resources, plus Viewer permissions

### 🟦 Viewer
* **Who:** Stakeholders (execs, auditors, consultants)
* **Responsibilities:** Read-only dashboards and reports
* **Access Scope:** Read-only

---

## 🧾 Subscription Plan Tiers

| Plan       | Max Users | Features                                               |
| ---------- | --------- | ------------------------------------------------------ |
| Basic      | 1         | Limited features, file uploads only, no Billing Admin |
| Standard   | 10        | Full RBAC support, integrations                        |
| Enterprise | 100       | Multi-vendor/sub-tenant, unlimited uploads, SLAs      |

---

## 🏢 Multi-Tenancy & Domain Strategy

* **Parent tenants:** unique subdomains (`apple.carboniq.com`)
* **Sub-tenants:** nested subdomains (`orchard.apple.carboniq.com`)
* **Schema isolation:** each tenant/sub-tenant has own schema
* **Access rules:**
  * Parent tenants → own + sub-tenant schemas
  * Sub-tenants → own schema only
  * Cross-tenant access denied

---

## 🌱 Seed Data Overview

### Apple Inc. (Enterprise)
* Users: `admin@apple.com` → TENANT_ADMIN
* Sub-tenants: Orchard Apple, Summit Apple, Harbor Apple

### Orange Ltd. (Standard)
* Users: `admin@orange.com` → TENANT_ADMIN
* Sub-tenants: Grove Orange, Horizon Orange

### Peanut Corp. (Basic)
* Users: `admin@peanut.com` → TENANT_ADMIN
* No sub-tenants
