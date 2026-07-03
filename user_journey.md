d d# CarbonIQ — User Journeys & Functional Permissions

**Version:** 1.0
**Date:** 2026-07-03
**Scope:** MVP (Scope 2 Emissions Module)

---

## 📋 Table of Contents

1. [User Personas Overview](#-user-personas-overview)
2. [Functional Permission Matrix](#-functional-permission-matrix)
3. [End-to-End User Journeys](#-end-to-end-user-journeys)
   - [SME Owner / Operator](#1-sme-owner--operator)
   - [SME Sustainability / ESG Manager](#2-sme-sustainability--esg-manager)
   - [Energy Advisor / Sustainability Consultant](#3-energy-advisor--sustainability-consultant)
   - [Accountant / Bookkeeper](#4-accountant--bookkeeper)
   - [External Auditor](#5-external-auditor)
   - [Customer Support / Success](#6-customer-support--success)
   - [Platform Admin (Super Admin)](#7-platform-admin-super-admin)
   - [Data / ML Operations](#8-data--ml-operations)
   - [API / Integration User](#9-api--integration-user-machine-to-machine)
   - [Regulator / Climate Active Reviewer](#10-regulator--climate-active-reviewer)
4. [Cross-Cutting User Flows](#-cross-cutting-user-flows)
5. [Out-of-Scope for MVP](#-out-of-scope-for-mvp)

---

## 👥 User Personas Overview

| # | Persona | Type | Primary Goal |
|---|---------|------|--------------|
| 1 | **SME Owner / Operator** | External | Report Scope 2 emissions for my business with minimal effort |
| 2 | **SME Sustainability / ESG Manager** | External | Manage ongoing emissions reporting across multiple sites/periods |
| 3 | **Energy Advisor / Sustainability Consultant** | External | Manage CarbonIQ for multiple SME clients |
| 4 | **Accountant / Bookkeeper** | External | Access Scope 2 data for financial/ESG reporting |
| 5 | **External Auditor** | External | Verify emissions reports and offset attribution |
| 6 | **Customer Support / Success** | Internal | Help users troubleshoot and resolve issues |
| 7 | **Platform Admin (Super Admin)** | Internal | Manage platform, users, billing, and system health |
| 8 | **Data / ML Operations** | Internal | Monitor data pipelines, model accuracy, and emissions factors |
| 9 | **API / Integration User** | External (machine) | Integrate CarbonIQ data into external systems (ERP, accounting) |
| 10 | **Regulator / Climate Active Reviewer** | External | Review submitted climate disclosures |

---

## 🔐 Functional Permission Matrix

Legend: ✅ Full | 🔶 Scoped | 👁️ Read-only | ❌ No access

| Functionality | SME Owner | ESG Mgr | Advisor | Accountant | Auditor | Support | Admin | DataOps | API User | Regulator |
|--------------|:---------:|:-------:|:-------:|:----------:|:-------:|:-------:|:-----:|:-------:|:--------:|:---------:|
| **Account & Access** |
| Sign up | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ (internal) | ❌ | ❌ | ❌ |
| Sign in | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (token) | ✅ (link) |
| Reset password | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage own profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| MFA setup | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Invite team members | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Organization Management** |
| Create organization | ✅ | ✅ | ✅ (for clients) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Edit org details | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Add multiple sites | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| **Energy Data Ingestion** |
| Upload smart meter CSV (NEM12) | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ✅ (API) | ❌ |
| Upload energy bill (OCR) | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Manual kWh entry | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ✅ (API) | ❌ |
| Connect smart meter API | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| View ingestion history | ✅ | ✅ | ✅ (clients) | ✅ (read) | 👁️ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Renewable Energy & Offsets** |
| Upload GreenPower contract | ✅ | ✅ | ✅ (clients) | ❌ | 👁️ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Upload REC/LGC certificate IDs | ✅ | ✅ | ✅ (clients) | ❌ | 👁️ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Upload PPA metadata | ✅ | ✅ | ✅ (clients) | ❌ | 👁️ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Upload onsite solar data | ✅ | ✅ | ✅ (clients) | ❌ | 👁️ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| **Emissions Calculation & Reporting** |
| Run emissions calculation | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (trigger for user) | ✅ | ✅ | ✅ (API) | ❌ |
| View emissions dashboard | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (scoped) |
| View hourly emissions | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (scoped) |
| View source breakdown | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (scoped) |
| Edit estimation assumptions | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (view only) | ✅ | ✅ | ❌ | ❌ |
| Override calculated values | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Export & Reporting** |
| Export PDF report | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Export CSV report | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export Climate Active template | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Share report link | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | 🔶 (internal) | ✅ | ❌ | ❌ | ✅ (generate) |
| Schedule recurring reports | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **AI Assistant** |
| Ask AI agent questions | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View AI explanations | ✅ | ✅ | ✅ (clients) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Advisor-Specific** |
| View client portfolio | ❌ | ❌ | ✅ | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Switch between client orgs | ❌ | ❌ | ✅ | ❌ | ❌ | 🔶 (view only) | ✅ | ❌ | ❌ | ❌ |
| Bulk operations across clients | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| White-label reports | ❌ | ❌ | ✅ (paid tier) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Platform Administration** |
| Manage all users | ❌ | ❌ | ❌ | ❌ | ❌ | 🔶 (view) | ✅ | ❌ | ❌ | ❌ |
| Manage all organizations | ❌ | ❌ | ❌ | ❌ | ❌ | 🔶 (view) | ✅ | ❌ | ❌ | ❌ |
| Manage billing & subscriptions | ✅ (own) | ✅ (own) | ✅ (own) | ❌ | ❌ | 🔶 (view) | ✅ | ❌ | ❌ | ❌ |
| Access feature flags | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| View system logs | ❌ | ❌ | ❌ | ❌ | ❌ | 🔶 (limited) | ✅ | ✅ | ❌ | ❌ |
| Impersonate user | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (with audit log) | ✅ | ❌ | ❌ | ❌ |
| **Data Operations** |
| View data pipeline status | ❌ | ❌ | ❌ | ❌ | ❌ | 🔶 | ✅ | ✅ | ❌ | ❌ |
| Trigger data refresh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| View model accuracy metrics | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Update emission factors | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **API & Integrations** |
| Generate API keys | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Manage API keys | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Access REST API | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Access webhooks | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Audit & Compliance** |
| View audit trail | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ (scoped) |
| Lock report for audit | ✅ | ✅ | ✅ (clients) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Sign off on report | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## 🚀 End-to-End User Journeys

---

### 1. SME Owner / Operator

**Persona:** Jamie, 42, runs a mid-sized bakery in Melbourne. Has 2 retail locations and a small warehouse. Knows Scope 2 reporting is required by a major customer but has zero sustainability background.

#### Functional Capabilities
- Sign up / sign in / manage own account
- Create and manage own organization
- Invite team members (basic roles)
- Upload energy bills (OCR) and smart meter data (CSV)
- Manually enter kWh and tariff data
- Upload GreenPower, RECs, PPA, onsite solar data
- Run emissions calculations
- View emissions dashboard (Scope 2, source breakdown, offsets)
- Export PDF, CSV, Climate Active templates
- Ask AI agent questions about emissions
- Schedule recurring reports
- Manage own subscription/billing

#### End-to-End User Story

> **As Jamie**, an SME owner who needs to report Scope 2 emissions for a major customer contract,
> **I want** to upload my energy bills and get an audit-ready emissions report in under 10 minutes,
> **so that** I can meet my customer's sustainability requirements without hiring a consultant.

**Journey Steps:**

1. **Discovery & Signup**
   - Lands on CarbonIQ homepage from a Google search for "Scope 2 reporting Australia"
   - Clicks "Start Free Trial"
   - Signs up with email + password (or Google OAuth)
   - Receives verification email, clicks link
   - Completes onboarding wizard: business name, ABN, industry (bakery), location (VIC), number of sites (3)

2. **Profile Setup**
   - Adds 3 sites: Bakery Melbourne CBD, Bakery Richmond, Warehouse Footscray
   - For each site, enters NMI (National Meter Identifier) from latest bill
   - Selects tariff type (single rate, time-of-use, demand)
   - Sets reporting period: 1 July 2025 – 30 June 2026 (financial year)

3. **Data Ingestion — Bills**
   - Uploads 3 electricity bills as PDF (drag-and-drop)
   - OCR engine extracts: total kWh, billing period, NMI, tariff charges
   - System flags: "Bill for Warehouse Footscray is low resolution — please verify: 2,450 kWh?"
   - Jamie confirms or corrects
   - Same for gas bills (2 sites)
   - Dashboard shows: "3 of 6 bills processed ✓"

4. **Data Ingestion — Smart Meter (Optional)**
   - Downloads NEM12 file from retailer portal (Powershop)
   - Uploads to CarbonIQ
   - System validates format and ingests 17,520 half-hourly intervals
   - Message: "Interval data replaces bill estimates for higher accuracy"

5. **Renewable Energy Upload**
   - Bought GreenPower through Powershop last quarter
   - Uploads GreenPower certificate PDF
   - System extracts: 5,000 kWh GreenPower, Q3 2025
   - Also uploads 2 REC certificate IDs purchased from retailer

6. **Onsite Solar**
   - Has 10kW rooftop solar on warehouse
   - Manually enters: system size, install date, estimated annual generation
   - Or uploads inverter data CSV

7. **Run Calculation**
   - Clicks "Calculate Emissions"
   - Backend pulls VIC grid mix (AEMO/OpenNEM) for the period
   - Applies location-based emission factors
   - Matches GreenPower + RECs against consumption hours
   - Generates residual emissions (what needs offsetting)
   - Processing completes in ~45 seconds

8. **Review Dashboard**
   - Sees:
     - Total Scope 2: 18.5 tCO₂e (location-based)
     - Total Scope 2: 12.3 tCO₂e (market-based, after GreenPower/REC matching)
     - Source breakdown: 62% coal, 18% gas, 12% wind, 8% solar
     - Offset coverage: 67% (GreenPower + RECs)
     - Residual: 6.2 tCO₂e to offset
   - Asks AI: "Why is my emission high in June?"
   - AI responds: "June had 3 cold days with high heating demand + low wind generation in VIC"

9. **Export Report**
   - Clicks "Export Climate Active Report"
   - Selects: PDF + CSV + Climate Active template
   - Downloads 3 files
   - Report shows: location-based vs market-based, hourly granularity, offset attribution

10. **Schedule Recurring Reports**
    - Sets quarterly auto-export to email
    - Configures: "Send to my accountant Sarah on 15th of each quarter"

11. **Customer Submission**
    - Forwards PDF to major customer as proof of Scope 2 reporting
    - Customer accepts ✓

12. **Billing & Renewal**
    - Receives monthly subscription invoice
    - Auto-renews after 12 months unless cancelled

---

### 2. SME Sustainability / ESG Manager

**Persona:** Priya, 35, ESG Manager at a mid-size tech company (150 employees, 2 offices). Responsible for all sustainability reporting including Scope 1, 2, 3. Currently uses Excel.

#### Functional Capabilities
- All SME Owner capabilities
- Manage multiple sites in one organization
- Recurring/quarterly reporting workflows
- Team member management with role-based access
- Bulk data operations across sites
- API access for internal integrations
- Advanced AI queries and analytics
- White-label reports (if paid tier)
- Custom date ranges and reporting periods

#### End-to-End User Story

> **As Priya**, an ESG Manager who runs quarterly sustainability reporting for my company,
> **I want** to automate Scope 2 calculations across all our sites and integrate with our existing ESG dashboard,
> **so that** I can produce Climate Active-ready reports without manual data crunching every quarter.

**Journey Steps:**

1. **Account Creation (via company domain)**
   - Signs up with work email
   - Creates organization: "TechCorp Pty Ltd"
   - Adds ABN, industry code, fiscal year end

2. **Team Setup**
   - Invites 2 colleagues: Finance Lead (accountant role), Operations Manager (SME Owner role)
   - Assigns permissions: Finance Lead sees only cost & emissions data; Ops Manager uploads meter data

3. **Multi-Site Configuration**
   - Adds 4 sites: Sydney HQ, Melbourne Office, Brisbane Office, Perth Office
   - For each: NMI, address, tariff type, primary business activity

4. **Bulk Data Upload**
   - Q1 close — uploads 4 electricity bills + 4 gas bills simultaneously (batch)
   - System processes all in parallel (~30 sec each)
   - Also pulls interval data via API for Sydney (largest site) automatically

5. **Renewable Portfolio**
   - Sydney HQ: 100kW solar + 50% GreenPower
   - Melbourne: 30kW solar + corporate PPA
   - Brisbane: GreenPower only
   - Perth: grid only
   - Uploads all certificates, contracts, inverter data

6. **Run Quarterly Calculation**
   - Selects reporting period: Q1 2026 (Jan–Mar)
   - Runs calculation across all sites
   - Compares to Q4 2025 (auto-generated trend chart)

7. **Multi-Site Dashboard Review**
   - Sees aggregated Scope 2: 45.2 tCO₂e across all sites
   - Drill-down per site:
     - Sydney: 18.5 tCO₂e (62% renewable matched)
     - Melbourne: 12.3 tCO₂e (78% renewable matched — PPA)
     - Brisbane: 9.8 tCO₂e (45% renewable matched)
     - Perth: 4.6 tCO₂e (0% renewable matched)
   - Source breakdown across portfolio

8. **AI Analysis**
   - Asks: "Which site has the highest emission intensity per employee?"
   - AI identifies Perth (no renewables, lower occupancy)
   - Asks: "What's the payback period for adding solar to Perth?"
   - AI uses solar irradiance + tariff data to estimate

9. **Integration Setup**
   - Generates API key for internal ESG dashboard
   - Configures webhook: POST emissions data to dashboard daily
   - Tests connection

10. **Climate Active Submission Prep**
    - Selects reporting boundary: "All sites, operational control"
    - Generates Climate Active PDF with:
      - Location-based Scope 2
      - Market-based Scope 2
      - Dual reporting (required by Climate Active)
      - Renewable energy attribution evidence
      - Audit trail
    - Submits to Climate Active via their portal (manual upload)

11. **Quarterly Recurring Setup**
    - Configures: auto-calculate on 5th of each quarter month
    - Auto-export PDF to leadership email list
    - Slack notification on completion

12. **Year-End Audit Prep**
    - Locks Q4 report (no further edits)
    - Generates auditor access link
    - Shares with external auditor

---

### 3. Energy Advisor / Sustainability Consultant

**Persona:** Marcus, 48, runs a boutique sustainability consulting firm. Manages Scope 2/3 reporting for ~25 SME clients. Currently does everything manually in Excel.

#### Functional Capabilities
- All Advisor-level capabilities (multi-tenant)
- Manage multiple client organizations from one account
- Switch between client orgs seamlessly
- Bulk operations across clients
- White-label reports with own branding
- Client billing management (pass-through or direct)
- Template library for common SME types
- Bulk client onboarding
- Advisor analytics (client portfolio emissions rollup)

#### End-to-End User Story

> **As Marcus**, a sustainability consultant managing Scope 2 reporting for 25 SME clients,
> **I want** a single dashboard where I can run emissions calculations across my entire client portfolio,
> **so that** I can scale my practice without hiring more analysts.

**Journey Steps:**

1. **Advisor Signup**
   - Signs up as "Advisor" account type (different from SME)
   - Provides: firm name, ABN, professional certifications (e.g., CEnvP)
   - Selects plan: Advisor Pro (25 clients, white-label, API access)

2. **Client Onboarding (Bulk)**
   - Creates 25 client organizations (one per SME)
   - For each: sends invitation email to client contact
   - Client signs up and links to Marcus's advisor account
   - Marcus gains access to each client's data

3. **Template Library**
   - Creates a "Standard Café SME" template with default assumptions
   - Creates a "Standard Office SME" template
   - Creates a "Standard Light Industrial" template
   - Applies templates to new clients during onboarding

4. **Bulk Data Collection**
   - Sends email blast to all clients: "Please upload your latest bill"
   - Monitors ingestion status across portfolio:
     - 18 of 25 clients uploaded ✓
     - 5 pending reminder
     - 2 escalated (OCR failed)
   - For escalated clients: manually enters kWh from bills sent via email

5. **Portfolio Calculation**
   - Selects all 25 clients → "Calculate Q1 2026"
   - System processes in parallel
   - Results appear in portfolio dashboard:
     - Total portfolio emissions: 425 tCO₂e
     - Average emissions per client: 17 tCO₂e
     - Renewable coverage: 52% average
     - Top 5 emitters flagged

6. **Client Report Generation**
   - Selects individual client → generates white-label report
   - Marcus's branding appears on PDF (logo, contact details)
   - Adds consultant notes section
   - Sends to client via CarbonIQ email

7. **Advisor Analytics**
   - Views portfolio rollup:
     - Total emissions under management
     - YoY trends per client
     - Renewable coverage trends
     - Clients approaching Climate Active threshold
   - Identifies upsell opportunities (e.g., "Client X has 0% renewables — pitch solar")

8. **Bulk Client Communication**
   - Sends quarterly newsletter to all clients with their summary stats
   - Schedules annual review meeting reminders

9. **Direct Client Billing (Optional)**
   - Configures: clients pay Marcus directly for CarbonIQ access
   - Marcus manages subscription on their behalf
   - Or: clients pay CarbonIQ, Marcus gets referral commission

10. **Year-End Portfolio Summary**
    - Generates annual portfolio summary for own accounting
    - Exports CSV for own ESG reporting (consulting firm itself)

---

### 4. Accountant / Bookkeeper

**Persona:** Sarah, 38, accountant at a mid-tier firm. Handles financial + ESG reporting for 15 SME clients. Just needs read access to Scope 2 numbers.

#### Functional Capabilities
- Sign in / manage own profile
- View Scope 2 emissions for assigned clients (read-only)
- Export consumption + emissions data (PDF, CSV)
- No data ingestion, no editing, no offset management

#### End-to-End User Story

> **As Sarah**, an accountant who needs Scope 2 emission data for my clients' annual ESG disclosures,
> **I want** read-only access to their CarbonIQ data so I can pull numbers into their financial reports,
> **so that** I can complete their annual filings without chasing down separate sustainability consultants.

**Journey Steps:**

1. **Invitation & Signup**
   - Client (SME Owner) invites Sarah via email
   - Sarah receives link: "Jamie from BakeryCo has granted you access"
   - Creates CarbonIQ account
   - Verifies identity (MFA for security)

2. **Read-Only Dashboard**
   - Logs in, sees: list of organizations she has access to
   - Selects "BakeryCo"
   - Sees emissions dashboard (read-only)
   - Cannot upload data, cannot edit assumptions

3. **Data Pull for Annual Filing**
   - Selects reporting period: FY2025-26
   - Exports:
     - Total Scope 2 (location-based)
     - Total Scope 2 (market-based)
     - Renewable energy attribution
     - Offset summary
   - Downloads CSV + PDF

4. **Cross-Reference with Financials**
   - Imports CSV into accounting software (Xero, MYOB)
   - Matches energy costs from P&L with emissions
   - Adds Scope 2 line to ESG disclosure

5. **Client Communication**
   - Notes any anomalies (e.g., "BakeryCo emissions up 20% YoY — investigate")
   - Emails client with question (outside CarbonIQ)

---

### 5. External Auditor

**Persona:** Dr. Chen, 52, lead auditor at a climate assurance firm. Verifies Scope 2 reports for Climate Active certification.

#### Functional Capabilities
- Sign in via secure access link
- View specific reports (read-only, immutable)
- Access full audit trail
- Download source data and methodology docs
- Sign off / flag concerns on reports
- Generate verification certificates

#### End-to-End User Story

> **As Dr. Chen**, an external auditor verifying a client's Climate Active submission,
> **I want** read-only access to their locked CarbonIQ report with full data lineage,
> **so that** I can verify the calculations and renewable attribution are accurate.

**Journey Steps:**

1. **Access Link Received**
   - Receives secure access link from client (Priya, ESG Manager)
   - Link valid for 30 days, scoped to specific report
   - MFA verification required

2. **Report Review**
   - Logs in, sees: locked report for TechCorp Q1 2026
   - Reviewing view shows:
     - Total Scope 2 (location + market)
     - Hourly emissions data
     - Renewable energy attribution
     - Source data (uploaded bills, meter files, RECs)
     - Methodology used (AEMO data source, emission factors)
     - Audit trail (every edit, every calculation run)

3. **Verification Checks**
   - Cross-checks uploaded bill kWh vs. extracted kWh
   - Verifies REC certificate IDs against GreenPower registry
   - Confirms emission factors match current DCCEEW values
   - Reviews AI estimation accuracy (if backcasting used)
   - Checks all assumptions are documented

4. **Flag Concerns**
   - Notes: "GreenPower for Sydney appears to be claimed twice — once in GreenPower contract, once in REC upload"
   - Submits clarification request via platform
   - Priya receives notification, corrects double-counting

5. **Sign-Off**
   - Once satisfied, marks report as "Audited ✓"
   - Generates verification certificate
   - Submits to Climate Active alongside client's disclosure

6. **Archive Access**
   - Audit trail preserved for 7 years (regulatory requirement)
   - Can re-access via same link for spot checks

---

### 6. Customer Support / Success

**Persona:** Alex, 28, Customer Success at CarbonIQ. Handles 50-80 support tickets per week.

#### Functional Capabilities
- Sign in to internal admin console
- View any user account (with audit log)
- View any organization
- Trigger re-processing for user (e.g., re-run OCR, re-calculate)
- Impersonate user (with audit log entry)
- View system status, recent errors
- Cannot delete user data, cannot change billing, cannot access feature flags

#### End-to-End User Story

> **As Alex**, a Customer Success rep handling a user complaint about wrong emissions numbers,
> **I want** to view the user's account, see what data they uploaded, and trigger a re-calculation,
> **so that** I can diagnose and resolve their issue without needing engineering help.

**Journey Steps:**

1. **Ticket Received**
   - Ticket from Jamie: "My emissions are way too high — it says 50 tCO₂e but should be ~15 tCO₂e"

2. **Investigation**
   - Searches for Jamie's account in admin console
   - Views his organization: BakeryCo
   - Sees uploaded data:
     - 3 electricity bills
     - OCR extracted: 45,000 kWh (but Jamie manually confirmed)
   - Notices: One bill was for the warehouse + retail combined (3-phase meter, but Jamie confirmed)
   - Checks ingestion logs: OCR confidence was 60% for that bill — flagged but Jamie overrode

3. **Impersonation**
   - Uses "View as user" feature (creates audit log entry)
   - Sees exactly what Jamie sees in his dashboard
   - Confirms: emissions calculation includes that 45,000 kWh figure

4. **Diagnosis**
   - Identifies: Bill was likely misread by OCR — actual kWh is 8,000, not 45,000
   - Contacts Jamie via email: "Can you re-upload the warehouse bill? The OCR may have misread the total"

5. **Re-processing**
   - Once Jamie uploads correct bill
   - Triggers manual re-calculation from admin console
   - Emissions recalculated: 17 tCO₂e ✓

6. **Resolution & Follow-up**
   - Marks ticket as resolved
   - Adds tag: "OCR misread — needs higher res scan"
   - Logs feature request: "Add OCR confidence threshold warning before user confirmation"

---

### 7. Platform Admin (Super Admin)

**Persona:** Raj, 35, engineering lead / co-founder at CarbonIQ. Manages platform health and user base.

#### Functional Capabilities
- Full system access (all features, all data)
- Create / edit / delete users
- Create / edit / delete organizations
- Manage billing and subscriptions
- Set and toggle feature flags
- View all system logs
- Manage data pipeline configurations
- Update emission factors globally
- Access audit trail across all orgs
- Impersonate any user (with audit log)

#### End-to-End User Story

> **As Raj**, a platform admin managing CarbonIQ's infrastructure and user base,
> **I want** a comprehensive admin console to manage users, billing, feature flags, and system health,
> **so that** I can keep the platform running smoothly and respond to incidents quickly.

**Journey Steps:**

1. **Daily Health Check**
   - Logs in to admin console
   - Reviews dashboard:
     - Active users: 1,247 (+23 this week)
     - Organizations: 892
     - API uptime: 99.97%
     - Data pipeline status: ✓ AEMO feed fresh, ✓ OpenNEM feed fresh, ⚠️ OCR queue backed up (12 min)
     - Revenue MRR: $47,500

2. **User Management**
   - Receives request: "Suspend account for non-payment"
   - Searches user, views billing history
   - Suspends account (user can still view data, cannot run new calculations)
   - Sends automated suspension email

3. **Feature Flag Management**
   - Planning to release "AI Forecast" feature (v2) to beta users
   - Enables flag: "ai_forecast" for 50 selected orgs
   - Monitors adoption metrics

4. **Incident Response**
   - Alert: "AEMO feed failing — last successful sync 4 hours ago"
   - Investigates pipeline logs
   - Identifies: AEMO API rate limit hit during peak load
   - Implements rate limit backoff, restarts pipeline
   - Marks incident resolved, adds postmortem doc

5. **Emission Factor Update**
   - DCCEEW publishes new annual emission factors
   - Updates database via admin tool
   - Triggers re-calculation for all orgs (background job)
   - Notifies users: "Your reports have been updated with 2025-26 emission factors"

6. **Billing Review**
   - Reviews failed payments for the month
   - Sends dunning emails
   - Cancels accounts after 60 days non-payment

---

### 8. Data / ML Operations

**Persona:** Lin, 32, ML engineer at CarbonIQ. Owns the emissions estimation engine and OCR pipeline.

#### Functional Capabilities
- View data pipeline status
- Trigger data refreshes
- View model accuracy metrics
- Update emission factors
- Access raw data for debugging
- Cannot manage users, billing, or orgs
- Read-only access to anonymized user data for model training

#### End-to-End User Story

> **As Lin**, an ML engineer responsible for the emissions estimation engine,
> **I want** visibility into model accuracy and data pipeline health,
> **so that** I can maintain the 95% accuracy target and respond to data drift.

**Journey Steps:**

1. **Daily Model Monitoring**
   - Opens DataOps dashboard
   - Reviews metrics:
     - kWh → CO₂e conversion accuracy: 96.2% (above 95% target ✓)
     - OCR extraction accuracy: 92% (below 95% target ⚠️)
     - Bill-to-kWh inference accuracy: 94% (acceptable)
     - Data freshness: AEMO 2hr ago ✓, OpenNEM 4hr ago ✓

2. **Drift Detection**
   - Notices: OCR accuracy dropped from 95% to 92% over last month
   - Drills into error breakdown:
     - Most failures on gas bills (new format from AGL)
     - Multi-page bills failing
   - Triggers retraining job with new samples

3. **Emission Factor Refresh**
   - Q2 starts, pulls latest DCCEEW emission factors
   - Validates against previous quarter (sanity check)
   - Deploys to production
   - Triggers background re-calculation for all orgs

4. **AEMO Feed Investigation**
   - Alert: SWIS data missing for last 6 hours
   - Checks AEMO status page: scheduled maintenance
   - Implements graceful degradation: system uses last-known mix + warning banner
   - Once feed resumes, backfills missing hours

5. **Model Improvement**
   - Reviews feedback from support tickets tagged "wrong emissions"
   - Identifies pattern: bakery/cafe businesses have unusual load profiles
   - Adds industry-specific load profile templates
   - Runs A/B test: 50% on new model, 50% on old
   - New model shows 97.1% accuracy vs 95.8% old
   - Rolls out new model to 100%

---

### 9. API / Integration User (Machine-to-Machine)

**Persona:** A Xero integration (representing Sarah's accounting software) that needs to pull emissions data into financial reports.

#### Functional Capabilities
- Authenticate via API key (OAuth or token)
- Read emissions data via REST API
- Receive webhooks for new calculations
- Cannot authenticate via UI login (machine account)

#### End-to-End User Story

> **As a Xero integration**, I need to retrieve BakeryCo's Scope 2 emissions data automatically,
> **so that** it can appear in the client's financial reporting without manual export.

**Journey Steps:**

1. **API Key Generation**
   - CarbonIQ generates service account for "Xero Integration"
   - Scoped permissions: read emissions data only
   - Returns API key (stored securely by Xero)

2. **Authentication**
   - Xero sends request: `GET /api/v1/orgs/{org_id}/emissions`
   - Header: `Authorization: Bearer {api_key}`
   - CarbonIQ validates, returns 200 OK

3. **Data Retrieval**
   - Xero pulls:
     ```json
     {
       "org_id": "bakeryco_123",
       "period": "2025-Q4",
       "scope2_location_based_tco2e": 18.5,
       "scope2_market_based_tco2e": 12.3,
       "renewable_coverage_pct": 67,
       "residual_tco2e": 6.2
     }
     ```

4. **Webhook Subscription**
   - Xero subscribes: `POST /webhooks/subscribe`
     - Event: `emissions.calculated`
     - URL: `https://xero.com/webhooks/carboniq`
   - When Jamie runs a new calculation, CarbonIQ POSTs to Xero
   - Xero ingests data into client's ESG module

5. **Rate Limit Handling**
   - Xero respects rate limits (e.g., 100 req/min)
   - Implements exponential backoff on 429 responses

---

### 10. Regulator / Climate Active Reviewer

**Persona:** A Climate Active assessor reviewing TechCorp's certification submission.

#### Functional Capabilities
- Access via secure shared link (no full account)
- View specific locked reports
- View methodology and source data
- Download Climate Active template
- Cannot edit, cannot upload, cannot access other reports

#### End-to-End User Story

> **As a Climate Active reviewer**, I need to verify TechCorp's Scope 2 submission against their claimed emissions,
> **so that** I can assess whether they meet certification requirements.

**Journey Steps:**

1. **Receive Submission**
   - TechCorp submits Climate Active disclosure via Climate Active portal (not CarbonIQ directly)
   - PDF report from CarbonIQ is attached as evidence

2. **Access Verification Link**
   - If auditor requires deeper access, receives secure link from TechCorp
   - Link valid for 60 days, scoped to one org, one period
   - MFA verification required

3. **Review**
   - Views:
     - Final emissions report
     - Source data (bills, meter files)
     - Methodology (which AEMO data, which emission factors)
     - Renewable attribution logic
   - Cross-checks against Climate Active technical requirements

4. **Verification Outcome**
   - Marks as: Approved / Needs Clarification / Rejected
   - Climate Active portal handles certification decision
   - CarbonIQ link expires after 60 days

---

## 🔄 Cross-Cutting User Flows

### A. Signup & Onboarding (All External Users)
1. Land on homepage
2. Click "Sign Up" → choose role (SME / Advisor / Accountant / Auditor)
3. Enter email + password (or OAuth)
4. Verify email
5. Complete role-specific onboarding wizard
6. MFA setup (encouraged, required for Advisor/Auditor)

### B. Forgot Password
1. Click "Forgot Password" on login
2. Enter email
3. Receive reset link (15-min expiry)
4. Set new password
5. MFA challenge if enabled

### C. MFA Setup
1. Profile → Security → Enable MFA
2. Scan QR code with authenticator app
3. Enter 6-digit code to verify
4. Save backup codes

### D. Team Invitation
1. Org admin invites email
2. Invitee receives email with signup link
3. Signup pre-filled with org context
4. Invitee selects role (within what admin allowed)
5. Admin receives confirmation

### E. Report Sharing
1. Report owner generates shareable link
2. Configure: expiry, password protection, scope (full report / summary only)
3. Send link to recipient
4. Recipient views without account (or with MFA-gated account)

### F. Data Export
1. Select report → Export
2. Choose format: PDF / CSV / Climate Active template
3. Apply date range / scope filters
4. Download (or schedule email delivery)

### G. AI Agent Query
1. From dashboard or report, click "Ask AI"
2. Type question in natural language
3. AI retrieves relevant data, computes, explains
4. User can drill down or ask follow-up
5. AI conversation logged for audit

---

## 🚫 Out-of-Scope for MVP

The following are explicitly noted as out-of-scope for v1 but may inform user role design:

- Scope 1 / Scope 3 emissions (different methodology, different data sources)
- Offset purchasing (read-only registry integration only)
- Full Climate Active certification submission (we provide templates, user submits manually)
- Blockchain audit trail (use traditional append-only logs)
- Consultant marketplace
- Mobile native apps
- Real-time emissions monitoring (live meter feeds)
- Forecasting and scenario modeling (v2)

---

## 📝 Notes for Implementation

1. **Multi-tenancy model:** Advisor accounts can access multiple client orgs. All data access must be scoped via `org_id` + `user_role`. Use row-level security in PostgreSQL.

2. **Audit trail:** Every emissions calculation, data edit, override, and access by Auditor/Support/Admin must be logged immutably. Consider event sourcing for emissions data specifically.

3. **Impersonation:** Support and Admin can impersonate users, but every action must be logged with `impersonated_by` field. Consider session timeout (15 min).

4. **Data privacy:** Energy consumption data is commercially sensitive. Ensure encryption at rest, in transit, and field-level encryption for PII (NMI, address).

5. **API rate limits:** Implement tiered rate limits (free: 100/hr, pro: 1000/hr, enterprise: custom).

6. **Report locking:** Once a report is submitted to Climate Active or locked for audit, it becomes immutable. Users can create a "copy" to make further changes.

7. **Role hierarchy:** Some roles are additive (Advisor can do everything an SME Owner can, plus multi-client). Use permission inheritance rather than flat role lists.

---

**End of document**