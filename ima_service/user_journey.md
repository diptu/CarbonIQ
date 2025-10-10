# RBAC User Journeys & Test Cases — FastAPI / SQLAlchemy

This file defines **RBAC user journeys** and detailed **test cases**
for authentication, CRUD, role assignment, and permission enforcement.

---

## 1️⃣ Authentication & Login

| # | Test Case                          | User                        | Tenant          | Result  | HTTP | Description                             |
| - | ---------------------------------- | --------------------------- | --------------- | ------- | ---- | --------------------------------------- |
| 1 | Login as admin                     | admin@apple.com             | Apple Inc.      | Success | 200  | Admin can log in                         |
| 2 | Login as billing user              | billing@orchard.apple.com   | Orchard Apple   | Success | 200  | Billing user login                       |
| 3 | Login as admin in other tenant     | admin@orange.com            | Grove Orange    | Success | 200  | Admin logs into own tenant               |
| 4 | Login as basic-plan admin          | admin@peanut.com            | Peanut Corp.    | Success | 200  | Basic-plan admin login                   |
| 5 | Non-existent tenant admin          | admin@peanut.com            | Non-existent    | Fail    | 403  | Admin cannot log in                       |
| 6 | Invalid password                   | admin@apple.com             | Apple Inc.      | Fail    | 401  | Authentication fails with wrong pass     |
| 7 | Inactive user                      | inactive@apple.com          | Apple Inc.      | Fail    | 403  | Inactive users denied                     |

---

## 2️⃣ User Listing / Read

| #  | Test Case                      | User                        | Tenant          | Result                       | HTTP | Description                        |
| -- | ------------------------------ | --------------------------- | --------------- | ---------------------------- | ---- | ---------------------------------- |
| 8  | List users in own tenant       | billing@orchard.apple.com   | Orchard Apple   | Only Orchard Apple users      | 200  | Tenant sees own users only         |
| 9  | List users in parent tenant    | billing@orchard.apple.com   | Apple Inc.      | Fail                         | 403  | Cannot fetch parent tenant users  |
| 10 | List users in unrelated tenant | billing@orchard.apple.com   | Orange Ltd.     | Fail                         | 403  | Cannot fetch unrelated tenants    |
| 11 | List users as admin            | admin@apple.com             | Apple Inc.      | Own + child tenants included | 200  | Admin sees all child tenants       |
| 12 | List users as super-admin      | superadmin@carboniq.com     | All             | All users                     | 200  | Super-admin sees all tenants       |

---

## 3️⃣ User Creation

| #  | Test Case                  | User                 | Tenant        | Role   | Result | HTTP | Description                                    |
| -- | -------------------------- | ------------------  | ------------- | ------ | ------ | ---- | ---------------------------------------------- |
| 13 | Create user in own tenant   | admin@apple.com      | Apple Inc.    | MEMBER | Success | 201  | Admin creates users                             |
| 14 | Create user in child tenant | admin@apple.com      | Orchard Apple | MEMBER | Success | 201  | Parent tenant admin can create child users    |
| 15 | Create user in unrelated    | admin@apple.com      | Orange Ltd.   | N/A    | Fail    | 403  | Cannot create users in unrelated tenants     |
| 16 | Duplicate user               | admin@apple.com      | Apple Inc.    | MEMBER | Fail    | 400  | Duplicate user handled gracefully             |
| 17 | Basic-plan tenant creation   | admin@peanut.com     | Peanut Corp.  | MEMBER | Success | 201  | Standard permissions in basic tenant         |
| 18 | Invalid sub-tenant creation | admin@peanut.com     | Non-existent  | N/A    | Fail    | 403  | Cannot create users in invalid tenants       |
| 19 | Restricted role assignment   | billing@orchard.apple.com | Orchard Apple | ADMIN | Fail    | 403  | Non-admin cannot assign admin roles           |

---

## 4️⃣ Role Assignment & Mapping

| #  | Test Case                 | User                   | Tenant       | Role   | Result  | HTTP | Description                             |
| -- | ------------------------- | --------------------  | ------------ | ------ | ------- | ---- | --------------------------------------- |
| 20 | Assign role to new user    | admin@apple.com        | Apple Inc.   | VIEWER | Success | 200  | Default role assigned                    |
| 21 | Assign role outside scope  | billing@orchard.apple.com | Apple Inc. | ADMIN | Fail    | 403  | Cannot assign roles outside scope        |
| 22 | Duplicate role assignment  | Existing user-role     | —            | N/A    | Fail    | 400  | Duplicate entries handled                 |
| 23 | Verify role mapping        | Newly created user     | Tenant       | Default| Success | 200  | Exists in user_roles table               |
| 24 | Remove role from user      | admin@apple.com        | Apple Inc.   | N/A    | Success | 200  | Admin can revoke roles                   |
| 25 | Remove role outside tenant | admin@apple.com        | Orange Ltd.  | N/A    | Fail    | 403  | Cannot remove roles in unrelated tenant |

---

## 5️⃣ Permission Enforcement

| #  | Test Case                     | User                     | Action         | Result  | HTTP | Description                           |
| -- | ----------------------------- | ----------------------- | -------------- | ------- | ---- | ------------------------------------- |
| 26 | Access own tenant resources    | billing@orchard.apple.com | List documents | Success | 200  | Users access own tenant resources     |
| 27 | Access parent tenant resources | billing@orchard.apple.com | List documents | Fail    | 403  | Parent tenant blocked                  |
| 28 | Access unrelated tenant        | billing@orchard.apple.com | List documents | Fail    | 403  | Unrelated tenants blocked              |
| 29 | Admin action in child tenant   | admin@apple.com          | Create user    | Success | 201  | Admin can act in child tenant          |
| 30 | Restricted action as viewer    | viewer@apple.com         | Create user    | Fail    | 403  | Viewer cannot perform admin actions    |

---

## 6️⃣ Edge Cases & Security

| #  | Test Case                     | User                  | Tenant       | Result | HTTP | Description                               |
| -- | ----------------------------- | ------------------- | ------------ | ------ | ---- | ----------------------------------------- |
| 31 | Admin in non-existent tenant   | admin@ghost.com       | Non-existent | Fail   | 403  | Admin login blocked                        |
| 32 | Role escalation attempt        | billing@orchard.apple.com | N/A       | Fail   | 403  | Cannot elevate role via API               |
| 33 | Expired session/token          | Any user              | Any          | Fail   | 401  | Expired JWT blocks access                 |
| 34 | Delete user in own tenant      | admin@apple.com       | Apple Inc.   | Success| 200  | Admin can delete users in own tenant      |
| 35 | Delete user in unrelated tenant | admin@apple.com      | Orange Ltd.  | Fail   | 403  | Admin cannot delete users outside tenant  |
