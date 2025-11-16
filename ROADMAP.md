# Multi-Tenant RBAC Architecture --- Tenant Service Design

This document outlines the design for a hierarchical, schema-per-tenant
architecture using three core services: Auth, User, and Tenant Service.

------------------------------------------------------------------------

## 🌐 Overview

We implement **multi-tenant SaaS with hierarchical RBAC** where:

-   Each tenant gets its **own schema**.
-   Tenants may be **parent or child tenants**.
-   **Parent tenants can access their own + child tenants' data**.
-   **Child tenants can only access themselves**.
-   Centralized auth & user management but tenant-linked permissions via
    Memberships.

------------------------------------------------------------------------

# 📁 Services

## 1. Auth Service

**Model: TokenBlacklist** - Stores revoked JWT refresh tokens. - Shared
across system.

    TokenBlacklist(id, jti, created_at, updated_at)

------------------------------------------------------------------------

## 2. User Service

Holds **global users**, roles, permissions:

    User(id, email, hashed_password, fullname, is_active)
    Role(id, name)
    Permission(id, name)
    UserRole(user_id, role_id)
    RolePermission(role_id, permission_id)

These users can belong to multiple tenants via Tenant Service.

------------------------------------------------------------------------

## 3. Tenant Service

### Core Models

    Tenant(id, name, parent_id, schema_name, status, plan)
    TenantDomain(id, tenant_id, domain)
    TenantMembership(id, tenant_id, user_id, role_id)

### Tenant Schema Naming Rules

-   Automatically generated:
    -   Parent tenant:\
        **apple → apple**
    -   Child tenant:\
        **orchard.apple → orchard_apple**

### Final Domain Format

`<schema>.carboniq.com`

### Example

  --------------------------------------------------------------------------
  Tenant Name      Parent   Domain                          Schema Name
  ---------------- -------- ------------------------------- ----------------
  Apple            NULL     apple.carboniq.com              apple

  Orchard.Apple    Apple    orchard_apple.carboniq.com      orchard_apple

  Peanut.Apple     Apple    peanut_apple.carboniq.com       peanut_apple
  --------------------------------------------------------------------------

------------------------------------------------------------------------



# 🧪 Test Cases

## Test 1 --- Parent Tenant Creation

**Input:** - name = `"Apple"`

**Expected:** - schema_name = `"apple"` - domain =
`"apple.carboniq.com"`

------------------------------------------------------------------------

## Test 2 --- Child Tenant Creation

**Input:** - name = `"Orchard"` - parent = `"Apple"`

**Expected:** - schema_name = `"orchard_apple"` - domain =
`"orchard_apple.carboniq.com"`

------------------------------------------------------------------------

## Test 3 --- Deep Hierarchy

Apple → Orchard.Apple → Sales.Orchard.Apple

**Expected:**

  Tenant    Schema
  --------- ---------------------
  Apple     apple
  Orchard   orchard_apple
  Sales     sales_orchard_apple

------------------------------------------------------------------------

## Test 4 --- Membership Permissions

Parent user should access: - parent tenant - all child tenants

Child user should access: - only its own tenant

------------------------------------------------------------------------

# 🚀 Summary

This architecture ensures:

-   Full **isolation** via schema-per-tenant.
-   **Hierarchical RBAC**.
-   **Automatic domain + schema generation**.
-   **Extensibility for future billing, usage metering, provisioning.**



# Mono-Repo Architecture Overview
```
mono_repo/
├── iam_service/             # Auth & RBAC
├── tenant_service/          # Tenant, org, membership
├── ingestion_service/       # Bill & meter ingestion (CSV/PDF)
├── ocr_service/             # OCR for PDF bills
├── normalization_service/   # Normalization & Data Quality
├── factor_service/          # Factor registry (AEMO/OpenNEM)
├── calculation_service/     # Interval-based calculations & backcasting
├── ai_service/              # AI estimation (kWh & load profiles)
├── renewables_service/      # REC, GreenPower, PPA attribution
├── offset_service/          # Offset catalog & REC uploads
├── reporting_service/       # PDF/CSV report generation
├── explainability_service/  # Explain consumption/emission anomalies
├── onboarding_service/      # Guided onboarding wizard
├── notification_service/    # Alerts (email/webpush)
├── gateway_service/         # API Gateway for routing + JWT validation
├── shared_libs/             # Shared JWT/RBAC/utils/db models
└── pyproject.toml
```
# Service-by-Service Plan
## A. IAM & Tenant Services

### Focus: Multi-tenant RBAC & user management
Tasks:

- Implement login, refresh, logout endpoints

- JWT-based auth + global/tenant roles

- Tenant/org CRUD

- Membership management for user-org links

- Tenant context propagation middleware
Endpoints:

    - POST /auth/login

    - POST /auth/refresh

    - POST /users/{id}/roles

    - POST /tenants, GET/PUT/
    - DELETE /tenants/{id}

    - POST /tenants/{tenant_id}/members

## B. Ingestion Service

### Focus: Bill & meter ingestion
Tasks:

- Upload CSV & PDF

- Store raw files in S3/local

- Validate file format & schema
Endpoints:

   - POST /upload/csv

  - POST /upload/pdf

  - GET /uploads/{file_id}

## C. OCR Service

### Focus: Extract text from PDF bills
Tasks:

- Tesseract OCR with preprocessing (grayscale/threshold)

- Store extracted text for downstream services
Endpoints:

    - POST /ocr/pdf

    - GET /ocr/{file_id}

## D. Normalization & Data Quality Service

### Focus: Standardize and validate ingested data
Tasks:

- Normalize dates, meter readings, bill amounts

- Validate schema, missing values, duplicates

- Generate validation reports
Endpoints:

    - POST /normalize

    - POST /validate

    - GET /validation/{batch_id}

E. Factor Service

### Focus: External intensity data
Tasks:

- Fetch CSV/API from AEMO/OpenNEM

- CRUD for factor registry

- Validate timestamps & schema
Endpoints:

    - POST /factors

    - GET /factors/{id}

    - PUT /factors/{id}

    - DELETE /factors/{id}

## F. Calculation Engine

### Focus: Interval-based energy metrics & backcasting
Tasks:

- Compute kWh, emissions per interval

- Store calculation results

- Support backcasting using historical data
Endpoints:

    - POST /calculate

    - GET /calculations/{interval_id}

## G. AI Estimation

### Focus: Estimate kWh from bills, infer load profiles
Tasks:

- ML model: bill → kWh

- Load profile inference

- Store & monitor AI predictions
Endpoints:

  - POST /estimate/bill

  - GET /estimate/{bill_id}

## H. Renewables Attribution

### Focus: REC, GreenPower, PPA attribution
Tasks:

- CRUD endpoints for RECs, GreenPower, PPA

- Validate attribution rules
Endpoints:

    - POST /attribution

    - GET /attribution/{id}

## I. Offset Catalog

### Focus: Manage offsets and REC uploads
Tasks:

- Upload and validate REC files

- CRUD for offsets and uploaded files
Endpoints:

    - POST /offsets

    - GET /offsets/{id}

    - POST /offsets/upload

## J. Reporting Service

### Focus: Generate PDF/CSV reports
Tasks:

- Aggregate data from attribution + offsets + consumption

- Schedule background reports

- Export to PDF/CSV
Endpoints:

    - GET /reports/{id}

    - POST /reports/schedule

## K. Explainability Agent

### Focus: Explain anomalies in consumption/emissions
Tasks:

- Rule-based / ML explanations

- Integrate API with frontend cards
Endpoints:

    - GET /explain/{metric_id}

## L. Onboarding Wizard

## Focus: Guided user onboarding
Tasks:

- Multi-step onboarding UI

- Store progress and preferences
Endpoints:

    - POST /onboarding/start

    - PUT /onboarding/progress

    - GET /onboarding/{user_id}

# #M. Notification Service

### Focus: Alerts and notifications
Tasks:

- Trigger email/webpush on events

- Frontend notification center integration
Endpoints:

    - POST /notifications

    - GET /notifications/{user_id}

# 3. Integration & Data Flow

```
[User/Frontend]
       │
       ▼
[API Gateway] --> JWT validated
       │
       ▼
+---------------------------+
| Tenant Service            |
| - Membership + RBAC       |
+---------------------------+
       │
       ▼
[Ingestion Service] --> [OCR Service] --> [Normalization Service] --> [Calculation Service] --> [AI Service]
       │                                                                      │
       ▼                                                                      ▼
[Factor Service] ----------------------------------------------------> [Renewables Attribution] --> [Offset Catalog]
       │                                                                      │
       ▼                                                                      ▼
                           [Reporting Service] <-----------------------------+
       │
       ▼
[Explainability Service] <-- triggered on anomaly / report
       │
       ▼
[Notification Service] <-- triggered events from ingestion, calculation, AI, reporting

```
