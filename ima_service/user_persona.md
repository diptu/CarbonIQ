# RBAC Sanity Test — Personas, Journeys, Seed Data & Multi-Tenancy Design

This repository contains a **comprehensive RBAC (Role-Based Access Control) sanity test setup** including:

* **User Personas** & their responsibilities
* **Role hierarchy** & permission inheritance
* **Multi-tenancy & domain strategy**
* **Seed data** for tenants, users, roles, and permissions
* **Test scenarios** for authentication, CRUD, and security edge cases

---

## 1️⃣ FastAPI / SQLAlchemy Models

* **Tenant**
* **User**
* **Role**
* **Permission**
* **UserRole**
* **RolePermission**

Refer to the `app/models/` folder for full definitions.

---

## 2️⃣ Seed Data Examples

Seed tenants, users, roles, and permissions using SQL:

```sql
-- Seed Tenants
INSERT INTO tenants (id, name, domain, schema_name)
VALUES
  (gen_random_uuid(), 'Apple Inc.', 'apple.carboniq.com', 'tenant_apple'),
  (gen_random_uuid(), 'Orchard Apple', 'orchard.apple.carboniq.com', 'tenant_orchard_apple'),
  (gen_random_uuid(), 'Orange Ltd.', 'orange.carboniq.com', 'tenant_orange'),
  (gen_random_uuid(), 'Peanut Corp.', 'peanut.carboniq.com', 'tenant_peanut')
ON CONFLICT (domain) DO NOTHING;

-- Seed Roles
INSERT INTO roles (id, name, description, is_system)
VALUES
  (gen_random_uuid(), 'TENANT_ADMIN', 'Tenant Administrator', true),
  (gen_random_uuid(), 'BILLING_ADMIN', 'Billing Administrator', true),
  (gen_random_uuid(), 'MEMBER', 'Regular Member', true),
  (gen_random_uuid(), 'VIEWER', 'Read-only User', true)
ON CONFLICT (name) DO NOTHING;

-- Seed Permissions
INSERT INTO permissions (id, name, description)
VALUES
  (gen_random_uuid(), 'users.create', 'Create users'),
  (gen_random_uuid(), 'users.read', 'Read users'),
  (gen_random_uuid(), 'users.update', 'Update users'),
  (gen_random_uuid(), 'users.delete', 'Delete users')
ON CONFLICT (name) DO NOTHING;
```

Seed users and assign roles similarly. Refer to the full SQL snippets in the repository.

---

## 3️⃣ Role Hierarchy

* **TENANT_ADMIN** → inherits `BILLING_ADMIN`, `MEMBER`, `VIEWER`
* **BILLING_ADMIN** → inherits `MEMBER`, `VIEWER`
* **MEMBER** → inherits `VIEWER`
* **VIEWER** → base read-only role

---

## 4️⃣ User Personas

| Persona       | Responsibilities                            | Access Scope               |
| ------------- | ------------------------------------------- | -------------------------- |
| Tenant Admin  | Invite/manage users, manage tenant settings | Full tenant control        |
| Billing Admin | Manage billing & invoices                   | Billing + Member + Viewer  |
| Member        | Regular team member                         | CRUD on resources + Viewer |
| Viewer        | Stakeholder with read-only access           | Read-only                  |

---

## 5️⃣ Subscription Plan Tiers

| Plan       | Max Active Users | Features                                   |
| ---------- | ---------------- | ------------------------------------------ |
| Basic      | 1                | Limited features, no Billing Admin         |
| Standard   | 10               | Full RBAC support, integrations            |
| Enterprise | 100              | Multi-vendor/sub-tenant, unlimited uploads |

---

## 6️⃣ Multi-Tenancy & Domain Strategy

* **Parent tenants** get unique subdomains: `apple.carboniq.com`, `orange.carboniq.com`, `peanut.carboniq.com`
* **Sub-tenants** get nested subdomains: `orchard.apple.carboniq.com`, `grove.orange.carboniq.com`
* **Schema isolation:** Each tenant/sub-tenant has its own schema
* **Access rules:**

  * Parent tenants can access own + sub-tenant schemas
  * Sub-tenants can only access their own schema
  * Cross-tenant access is denied

---

## 7️⃣ Seed Data Structure

### Apple Inc. (Enterprise)

* Users: `admin@apple.com` (TENANT_ADMIN)
* Sub-tenants: Orchard Apple, Summit Apple, Harbor Apple

### Orange Ltd. (Standard)

* Users: `admin@orange.com` (TENANT_ADMIN)
* Sub-tenants: Grove Orange, Horizon Orange

### Peanut Corp. (Basic)

* Users: `admin@peanut.com` (TENANT_ADMIN)
* No sub-tenants

---

## 8️⃣ Test Cases

### Authentication & Login

* Verify login success/failure for tenant admins, billing users, viewers, invalid credentials, and inactive users.

### User Listing / Read

* Verify tenant isolation and parent/sub-tenant visibility.

### User Creation

* Verify permissions for creating users within own tenant, sub-tenants, unrelated tenants, and duplicate users.

### Role Assignment & Mapping

* Verify correct role assignment, duplicate role handling, and permission enforcement.

### Permission Enforcement

* Verify access control for own tenant, parent tenant, unrelated tenants, admin actions, and viewer restrictions.

### Edge Cases & Security

* Verify login for non-existent tenants, role escalation attempts, expired sessions/tokens, and deletion of users within tenant boundaries.

---

> This setup ensures a complete RBAC + multi-tenancy environment for development, testing, and demonstration purposes.


1. Authentication & Login
   
| # | Test Case                          | User                        | Tenant          | Expected Result | Expected HTTP Status | Description                                     |
| - | ---------------------------------- | --------------------------- | --------------- | --------------- | -------------------- | ----------------------------------------------- |
| 1 | Login as admin                     | `admin@apple.com`           | `Apple Inc.`    | Success         | 200                  | Verify that admin can log in.                   |
| 2 | Login as billing user              | `billing@orchard.apple.com` | `Orchard Apple` | Success         | 200                  | Verify that billing user can log in.            |
| 3 | Login as admin in other tenant     | `admin@orange.com`          | `Grove Orange`  | Success         | 200                  | Admin should log in to their own tenant.        |
| 4 | Login as basic-plan admin          | `admin@peanut.com`          | `Peanut Corp.`  | Success         | 200                  | Verify login for basic-plan admin.              |
| 5 | Login as non-existent tenant admin | `admin@peanut.com`          | Non-existent    | Fail: 403       | 403                  | Admin cannot log in to a non-existent tenant.   |
| 6 | Login with invalid password        | `admin@apple.com`           | `Apple Inc.`    | Fail: 401       | 401                  | Ensure authentication fails for wrong password. |
| 7 | Login with inactive user           | `inactive@apple.com`        | `Apple Inc.`    | Fail: 403       | 403                  | Inactive users should be denied login.          |


2. User Listing / Read
   
| #  | Test Case                      | User                        | Tenant          | Expected Result            | Expected HTTP Status | Description                                       |
| -- | ------------------------------ | --------------------------- | --------------- | -------------------------- | -------------------- | ------------------------------------------------- |
| 8  | List users in own tenant       | `billing@orchard.apple.com` | `Orchard Apple` | Only Orchard Apple users   | 200                  | Tenant users see only their own users.            |
| 9  | List users in parent tenant    | `billing@orchard.apple.com` | `Apple Inc.`    | Fail: 403                  | 403                  | Users cannot fetch parent tenant users.           |
| 10 | List users in unrelated tenant | `billing@orchard.apple.com` | `Orange Ltd.`   | Fail: 403                  | 403                  | Users cannot fetch unrelated tenants.             |
| 11 | List users as admin            | `admin@apple.com`           | `Apple Inc.`    | All child tenants included | 200                  | Admin can view users in own tenant + sub-tenants. |
| 12 | List users as super-admin      | `superadmin@carboniq.com`   | All             | All users                  | 200                  | Super-admin can view users across all tenants.    |


3. User Creation

| #  | Test Case                                  | User                        | Tenant          | Expected Role           | Expected Result | Expected HTTP Status | Description                                                |
| -- | ------------------------------------------ | --------------------------- | --------------- | ----------------------- | --------------- | -------------------- | ---------------------------------------------------------- |
| 13 | Create user in own tenant                  | `admin@apple.com`           | `Apple Inc.`    | Default (MEMBER/VIEWER) | Success         | 201                  | Admin creates users in their tenant.                       |
| 14 | Create user in child tenant                | `admin@apple.com`           | `Orchard Apple` | Default                 | Success         | 201                  | Parent tenant admin can create users in child tenant.      |
| 15 | Create user in unrelated tenant            | `admin@apple.com`           | `Orange Ltd.`   | N/A                     | Fail: 403       | 403                  | Admin cannot create users in tenants they don’t belong to. |
| 16 | Create duplicate user                      | `admin@apple.com`           | `Apple Inc.`    | Default                 | Fail gracefully | 400                  | Duplicate users should be handled without crashing.        |
| 17 | Create user under Basic plan tenant        | `admin@peanut.com`          | `Peanut Corp.`  | Default                 | Success         | 201                  | Verify standard permissions in basic plan tenants.         |
| 18 | Create user under sub-tenant of Basic plan | `admin@peanut.com`          | Non-existent    | N/A                     | Fail: 403       | 403                  | Admin cannot create users in invalid tenants.              |
| 19 | Create user with restricted role           | `billing@orchard.apple.com` | `Orchard Apple` | ADMIN                   | Fail: 403       | 403                  | Users without admin cannot assign admin roles.             |


4. Role Assignment & Mapping

| #  | Test Case                         | User                        | Tenant        | Expected Role | Expected Result              | Expected HTTP Status | Description                                 |
| -- | --------------------------------- | --------------------------- | ------------- | ------------- | ---------------------------- | -------------------- | ------------------------------------------- |
| 20 | Assign role to new user           | `admin@apple.com`           | `Apple Inc.`  | VIEWER        | Success                      | 200                  | Default role is assigned correctly.         |
| 21 | Assign role outside allowed scope | `billing@orchard.apple.com` | `Apple Inc.`  | ADMIN         | Fail: 403                    | 403                  | Users cannot assign roles in other tenants. |
| 22 | Duplicate role assignment         | Existing user-role          | —             | N/A           | Fail gracefully              | 400                  | Ensure duplicate role entries are handled.  |
| 23 | Verify role mapping               | Newly created user          | Tenant        | Default role  | Exists in `user_roles` table | 200                  | Ensure proper mapping in DB.                |
| 24 | Remove role from user             | `admin@apple.com`           | `Apple Inc.`  | N/A           | Success                      | 200                  | Admin can revoke user roles.                |
| 25 | Remove role outside tenant scope  | `admin@apple.com`           | `Orange Ltd.` | N/A           | Fail: 403                    | 403                  | Cannot remove roles in unrelated tenants.   |


5. Permission Enforcement

| #  | Test Case                            | User                        | Action / Resource    | Expected Result | Expected HTTP Status | Description                                 |
| -- | ------------------------------------ | --------------------------- | -------------------- | --------------- | -------------------- | ------------------------------------------- |
| 26 | Access own tenant resources          | `billing@orchard.apple.com` | List documents/users | Success         | 200                  | Users can only access own tenant resources. |
| 27 | Access parent tenant resources       | `billing@orchard.apple.com` | List documents/users | Fail: 403       | 403                  | Permissions blocked for parent tenant.      |
| 28 | Access unrelated tenant resources    | `billing@orchard.apple.com` | List documents/users | Fail: 403       | 403                  | Permissions blocked for unrelated tenants.  |
| 29 | Perform admin action in child tenant | `admin@apple.com`           | Create user          | Success         | 201                  | Admin can perform actions in child tenant.  |
| 30 | Perform restricted action as viewer  | `viewer@apple.com`          | Create user          | Fail: 403       | 403                  | Viewers cannot perform admin-level actions. |


6. Edge Cases & Security

| #  | Test Case                         | User                        | Tenant        | Expected Result | Expected HTTP Status | Description                                     |
| -- | --------------------------------- | --------------------------- | ------------- | --------------- | -------------------- | ----------------------------------------------- |
| 31 | Admin in non-existent tenant      | `admin@ghost.com`           | Non-existent  | Fail: 403       | 403                  | Admin login blocked for invalid tenant.         |
| 32 | Role escalation attempt           | `billing@orchard.apple.com` | N/A           | Fail: 403       | 403                  | Users cannot elevate their role via API.        |
| 33 | Access with expired session/token | Any user                    | Any tenant    | Fail: 401       | 401                  | Expired JWT should block access.                |
| 34 | Delete user in own tenant         | `admin@apple.com`           | `Apple Inc.`  | Success         | 200                  | Admin can delete users in own tenant.           |
| 35 | Delete user in unrelated tenant   | `admin@apple.com`           | `Orange Ltd.` | Fail: 403       | 403                  | Admin cannot delete users outside their tenant. |
