# 🧑‍💼 User Service — Multi-Tenant SaaS RBAC Documentation

The User Service acts as the central identity & authorization engine for the entire multi-tenant SaaS architecture.
It stores and manages:

- Users

- Roles

- Permissions

- User–Role (relationships)

- Role–Permission (relationships)

This service connects with the Auth Service (for JWT issuance/validation) and the Tenant Service (for tenant membership & tenant-scoped roles).


1. Overview

The User Service provides a centralized RBAC system for all tenants in the platform.

Responsibilitie
| Component          | Responsibility                                                 |
| ------------------ | -------------------------------------------------------------- |
| **User Service**   | Stores global user accounts and global RBAC mapping            |
| **Auth Service**   | Issues, verifies, and blacklists JWT tokens                    |
| **Tenant Service** | Uses user IDs and role IDs to assign users to specific tenants |



Key Concepts

✔ Central users (login once, access many tenants)
✔ Global roles + permissions
✔ Each tenant uses TenantMembership(role_id) to link User → Tenant → Role
✔ Cached properties for fast permission lookup

2. Data Models

    2.1 User

    | Field           | Type    | Description               |
    | --------------- | ------- | ------------------------- |
    | id              | UUID    | Primary key               |
    | email           | String  | Unique login email        |
    | hashed_password | String  | bcrypt-hashed password    |
    | full_name       | String  | Optional name             |
    | is_active       | Boolean | User enabled/disabled     |
    | is_verified     | Boolean | Email verification status |
    | is_superuser    | Boolean | Global platform admin     |

    2.2 Role

    Represents a named RBAC role, e.g.:

    - TANENT_ADMIN

    - TANENT_BILLING

    - MEMBER

    - VIEWER


    | Field       | Type   | Description          |
    | ----------- | ------ | -------------------- |
    | id          | UUID   | Primary key          |
    | name        | String | Unique role name     |
    | description | Text   | Optional description |


    2.3 Permission

    Represents an atomic capability, e.g.:

    - document:create

    - user:invite

    - billing:read

    | Field       | Type   | Description           |
    | ----------- | ------ | --------------------- |
    | id          | UUID   | Primary key           |
    | name        | String | Unique permission key |
    | description | Text   | Optional details      |



    2.4 UserRole (Association Table)

    - Maps Users → Roles (global roles, not tenant-scoped).

    | Field   | Type | Description |
    | ------- | ---- | ----------- |
    | user_id | UUID | FK to User  |
    | role_id | UUID | FK to Role  |

    2.5 RolePermission (Association Table)

    - Maps Roles → Permissions.

    | Field         | Type | Description      |
    | ------------- | ---- | ---------------- |
    | role_id       | UUID | FK to Role       |
    | permission_id | UUID | FK to Permission |


    3. RBAC Logic

    3.1 Role Inheritance (Global)

    - User permissions are derived from:
    ```sql
    User → Roles → Permissions
    ```

    3.2 Permission Caching

    - The model provides cached properties:
    ```py
    user.roles_cached
    user.permissions_cached
    ```
    Used by:

        1. Auth Service when generating JWT

        2. Tenant Service when validating membership role

        3. API gateway for request-based authorization

    4. Integration With Tenant Service

    -  The User Service does NOT store tenant-specific roles or membership.

    Tenant Service stores:

       1. TenantMembership(user_id, role_id)

       2. TenantDomain

        3. Parent/child tenant structure

     So the flow becomes:
     ```sql
     User Service  →  Global RBAC
    Tenant Service →  Tenant mapping + Tenant roles
    Auth Service  →  Token issuance
    ```

    Example Multi-Tenant Scenario

        User: john@example.com
        John is:

        Owner of Apple

        Viewer of orchard.apple

        No access to tech.orrange
    | Tenant        | Role (TenantMembership) |
    | ------------- | ----------------------- |
    | Apple         | owner                   |
    | orchard.apple | viewer                  |
    | tech.orrange  | — (no membership)       |


    5. API Responsibilities

    5.1 User Endpoints

        Create user

        Update profile

        Activate/deactivate user

        Verify email

        Change password

    5.2 Role Endpoints

        Create role

        Assign/remove roles to users

        List roles

        Attach permissions to roles

    5.3 Permission Endpoints

        List permissions

        Create permissions

    5.4 Internal Endpoints (Consumed by Auth Service)

        GET /verify


    6. Example Data

    USERS

    | email                                           | roles  | active |
    | ----------------------------------------------- | ------ | ------ |
    | [admin@apple.com](mailto:admin@apple.com)       | admin  | True   |
    | [alice@apple.com](mailto:alice@apple.com)       | member | True   |
    | [viewer@orchard.com](mailto:viewer@orchard.com) | viewer | True   |

    ROLES

    | name   | description        |
    | ------ | ------------------ |
    | owner  | Full tenant access |
    | admin  | Manage users/docs  |
    | member | Basic contributor  |
    | viewer | Read-only          |

    Permissions

    | name            |
| --------------- |
| user.invite     |
| user.read       |
| document.create |
| document.update |
| billing.read    |
