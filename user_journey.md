# RBAC Sanity Test — User Personas & Journeys (with Subscription Plan Limits)

This document defines user personas for each role (`TENANT_ADMIN`, `BILLING_ADMIN`, `VIEWER`, `MEMBER`) and outlines **sanity test flows** to verify correct RBAC behavior.  
It also includes **multi-tier subscription plan restrictions** (Basic, Standard, Enterprise) with feature limits.

---

## 👤 User Personas

### 🟩 Tenant Admin
- **Who:** Primary owner/manager of a tenant.
- **Responsibilities:**
  - Manage tenant-level settings.
  - Invite, deactivate, and assign roles to users.
- **Access Scope:** Full control **within their tenant** only.
- **Plan Restriction Awareness:** Must ensure user invites **do not exceed subscription plan limits**.

---

### 🟧 Billing Admin
- **Who:** Finance/accounting staff responsible for payments.
- **Responsibilities:**
  - Manage billing, invoices, subscriptions.
  - View usage & cost breakdown.
- **Access Scope:** **Billing + usage data only**.
- **Plan Restriction Awareness:** Can **upgrade/downgrade subscription** to change user limits.

---

### 🟦 Viewer
- **Who:** Stakeholders (execs, auditors, consultants).
- **Responsibilities:**
  - View dashboards, reports, usage.
- **Access Scope:** **Read-only** access. Cannot modify anything.
- **Plan Restriction Awareness:** Does not affect subscription limits.

---

### 🟨 Member
- **Who:** Regular team members (engineers, analysts).
- **Responsibilities:**
  - Create, update, and use tenant resources.
- **Access Scope:** **CRUD on resources**, no billing or user management.
- **Plan Restriction Awareness:** Counted against **active user limit** of the tenant.

---

## 🧾 Subscription Plan Tiers

| Plan           | Max Users     | Features                                                                                 |
|----------------|---------------|------------------------------------------------------------------------------------------|
| **Basic**      | 5             | Limited features, file uploads only (small quota), **no Billing Admin role**.            |
| **Standard**   | 50            | Full RBAC support, all features enabled, access to integrations, monthly/yearly billing. |
| **Enterprise** | Unlimited     | Multi-vendor / sub-tenant / branch support, dedicated support, compliance (SOC2, HIPAA), SLAs, unlimited file uploads. |

> **Note:**  
> - User count = **active users only** (deactivated users don’t count).  
> - Upgrades unlock higher user caps, downgrades enforce limits on next billing cycle.  
> - Enterprise tenants can manage **multiple branches or sub-tenants** under the same parent organization.

---

## 🧪 Sanity Test Journeys

### 1. Tenant Admin Journey
✅ **Expected Allowed**
- Invite a new user **if under plan limit**.  
- Assign roles (`MEMBER`, `BILLING_ADMIN`, `VIEWER`).  
- Deactivate a user to free up slots.  
- Update tenant-wide settings.  
- (Enterprise only) Create/manage sub-tenants or branches.  

❌ **Expected Denied**
- Invite user if **max user limit exceeded** (returns `403 PLAN_LIMIT_EXCEEDED`).  
- Access billing if not assigned `BILLING_ADMIN`.  
- (Basic only) Cannot assign `BILLING_ADMIN`.  

---

### 2. Billing Admin Journey
✅ **Expected Allowed**
- View invoices & transaction history.  
- Update payment method.  
- View usage reports (user count vs. plan).  
- Upgrade/downgrade subscription.  

❌ **Expected Denied**
- Invite or remove users.  
- Change tenant-level settings.  
- Create or modify operational resources.  

---

### 3. Viewer Journey
✅ **Expected Allowed**
- View dashboards & reports.  
- View tenant resource metadata.  

❌ **Expected Denied**
- Modify or delete resources.  
- Manage billing.  
- Manage users/roles.  
- Affect subscription/user count.  

---

### 4. Member Journey
✅ **Expected Allowed**
- Create & edit resources (e.g., projects, datasets).  
- Upload files (limited by plan).  
- Collaborate with other members.  

❌ **Expected Denied**
- Manage users or roles.  
- Access billing.  
- Change tenant-wide settings.  
- (Basic only) File upload beyond quota.  

---

## ✅ Success Criteria
- Each persona can **only perform actions relevant to their role**.  
- Cross-tenant access is always denied.  
- Role escalation is not possible without `TENANT_ADMIN`.  
- Billing access remains isolated to `BILLING_ADMIN`.  
- **Subscription plan rules enforced consistently**:  
  - `TENANT_ADMIN` cannot exceed user cap.  
  - `BILLING_ADMIN` can adjust plan.  
  - Deactivations free up slots.  
  - File uploads restricted in **Basic**.  
  - **Enterprise** tenants can create/manage **sub-tenants or branches**.  
