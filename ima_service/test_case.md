# RBAC User Journeys & Test Cases — FastAPI / SQLAlchemy

This file defines detailed **test cases**
for authentication, CRUD, role assignment, and permission enforcement.

---

## 1️⃣ Authentication & Login and Refresh

| #  | Test Case                                   | User                                                          | Tenant                | Expect  | HTTP | Description                                            |
| -- | ------------------------------------------- | ------------------------------------------------------------- | --------------------- | ------- | ---- | ------------------------------------------------------ |
| 1  | Admin login                                 | [admin@apple.com](mailto:admin@apple.com)                     | Apple Inc.            | Success | 200  | Admin can log in successfully                          |
| 2  | Billing user login                          | [billing@orchard.apple.com](mailto:billing@orchard.apple.com) | Orchard Apple         | Success | 200  | Billing user login succeeds                            |
| 3  | Admin login into own tenant                 | [admin@orange.com](mailto:admin@orange.com)                   | Orange Ltd.           | Success | 200  | Admin logs into their own tenant                       |
| 4  | Basic-plan admin login                      | [admin@peanut.com](mailto:admin@peanut.com)                   | Peanut Corp.          | Success | 200  | Basic-plan admin login succeeds                        |
| 5  | Non-existent tenant login                   | [admin@mango.com](mailto:admin@mango.com)                     | Non-existent          | Fail    | 403  | Admin cannot log in to a non-existent tenant           |
| 6  | Invalid password login                      | [admin@apple.com](mailto:admin@apple.com)                     | Apple Inc.            | Fail    | 401  | Login fails with wrong password                        |
| 7  | Inactive user login                         | [inactive@apple.com](mailto:inactive@apple.com)               | Apple Inc.            | Fail    | 403  | Inactive users are denied login                        |
| 8  | Admin login to child tenant                 | [admin@apple.com](mailto:admin@apple.com)                     | Orchard Apple (child) | Success | 200  | Parent tenant admin can log in to child tenant         |
| 9  | Admin login to unrelated tenant             | [admin@apple.com](mailto:admin@apple.com)                     | Orange Ltd.           | Fail    | 403  | Admin cannot log in to unrelated tenant                |
| 10 | User login attempt with parent tenant token | [billing@orchard.apple.com](mailto:billing@orchard.apple.com) | Apple Inc.            | Fail    | 403  | Regular user cannot authenticate for a parent tenant   |
| 11 | Super-admin login without tenant header     | [superadmin@carboniq.com](mailto:superadmin@carboniq.com)     | —                     | Success | 200  | Super-admin can log in globally without tenant context |
| 12 | Login without tenant header                 | [admin@apple.com](mailto:admin@apple.com)                     | —                     | Fail    | 403  | Regular users cannot log in without tenant header      |
| 13 | Locked account after failed attempts        | [admin@apple.com](mailto:admin@apple.com)                     | Apple Inc.            | Fail    | 403  | Account locked due to repeated failed logins           |
| 14 | Refresh token with valid token              | Any user                                                      | Own tenant            | Success | 200  | Access + refresh tokens issued successfully            |
| 15 | Refresh token with invalid token            | Any user                                                      | Own tenant            | Fail    | 401  | Invalid refresh token is rejected                      |
| 16 | Refresh token from wrong tenant             | Any user                                                      | Different tenant      | Fail    | 403  | Tokens cannot be refreshed for another tenant          |
| 17 | Refresh token for inactive user             | [inactive@apple.com](mailto:inactive@apple.com)               | Apple Inc.            | Fail    | 403  | Inactive users cannot refresh tokens                   |
| 18 | Refresh token for revoked/blacklisted token | Any user                                                      | Own tenant            | Fail    | 401  | Revoked tokens cannot be used to refresh               |


