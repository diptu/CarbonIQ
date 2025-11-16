<!-- #Tenent_setvice/readme.md -->
# Multi-Tenant SaaS Architecture Documentation
1. Overview

    This project implements a multi-tenant SaaS platform with:

    RBAC (Role-Based Access Control)

    Parent-child hierarchical tenants

    Database-per-tenant (schema-per-tenant) isolation

    Separate Auth, User, and Tenant services

| Service        | Responsibility                                         | Database Type                              |
| -------------- | ------------------------------------------------------ | ------------------------------------------ |
| Auth Service   | JWT-based authentication, token blacklist              | Central                                    |
| User Service   | User, Role, Permission management                      | Central                                    |
| Tenant Service | Tenant hierarchy, domain management, tenant membership | Central metadata + tenant-specific schemas |

2. Tenant Service Models

2.1 Tenant

| Field       | Type   | Description                         |
| ----------- | ------ | ----------------------------------- |
| id          | UUID   | Primary key                         |
| name        | String | Tenant display name                 |
| schema_name | String | Automatically generated schema name |
| parent_id   | UUID   | FK to parent tenant (nullable)      |
| status      | Enum   | ACTIVE / INACTIVE                   |
| plan        | Enum   | FREE / BUSINESS / ENTERPRISE        |

2.2 TenantDomain
| Field       | Type    | Description                   |
| ----------- | ------- | ----------------------------- |
| id          | UUID    | Primary key                   |
| tenant_id   | UUID    | FK to Tenant                  |
| domain_name | String  | Domain or subdomain of tenant |
| is_primary  | Boolean | Primary domain flag           |
| verified    | Boolean | Domain verified flag          |

2.3 TenantMembership
| Field     | Type | Description                     |
| --------- | ---- | ------------------------------- |
| id        | UUID | Primary key                     |
| tenant_id | UUID | FK to Tenant                    |
| user_id   | UUID | FK to User (from User Service)  |
| role_id   | UUID | FK to Role (from User Service)  |
| is_owner  | Bool | True if user is top-level admin |

3. Schema Name Generation

    Rules:

    Schema name is based only on tenant name and parent (not domain)

    Format: <child>_<parent>

    Top-level parent: schema_name = sanitize(name)

    Child: schema_name = sanitize(child_name) + '_' + parent_schema

    Names are sanitized:

    Lowercase

    Spaces/dots → _

    Non-alphanumeric chars removed

    Ensures uniqueness by appending a counter if needed.

    Example:

    | Tenant Name   | Parent | Schema Name   |
    | ------------- | ------ | ------------- |
    | Apple         | NULL   | apple         |
    | Orchard.Apple | Apple  | orchard_apple |
    | Peanut.Apple  | Apple  | peanut_apple  |

4. Parent-Child Access Rules (RBAC)

| Tenant         | Can Access Schemas                 |
| -------------- | ---------------------------------- |
| Apple (parent) | apple, orchard_apple, peanut_apple |
| Orchard.Apple  | orchard_apple                      |
| Peanut.Apple   | peanut_apple                       |


5. Example Domain Mapping

| Tenant        | Domain                     |
| ------------- | -------------------------- |
| Apple         | apple.carboniq.com         |
| Orchard.Apple | orchard_apple.carboniq.com |
| Peanut.Apple  | peanut_apple.carboniq.com  |

- Domains are independent of schema names.
- Multiple domains per tenant are supported.
