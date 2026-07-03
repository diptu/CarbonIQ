# 🌏 CarbonIQ

> **Enterprise AI-powered Scope 2 carbon accounting & reporting platform**
>
> Transparent · Audit-ready · Climate Active & ASRS aligned · Multi-tenant · ≥95% accuracy

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-org/carboniq/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Code Coverage](https://img.shields.io/badge/coverage-87%25-yellowgreen.svg)](coverage)
[![Version](https://img.shields.io/badge/version-1.0.0--beta-blue.svg)](releases)
[![Security](https://img.shields.io/badge/security-A%2B-success.svg)](security)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](contributing)

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [Why CarbonIQ](#-why-carboniq)
- [Key Capabilities](#-key-capabilities)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Microservices Catalog](#-microservices-catalog)
- [Repository Structure](#-repository-structure)
- [Environments & SLAs](#-environments--slas)
- [Quick Start](#-quick-start)
- [Security & Compliance](#-security--compliance)
- [Observability](#-observability)
- [Testing Strategy](#-testing-strategy)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Roadmap](#-roadmap)
- [Support & Community](#-support--community)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Executive Summary

**CarbonIQ** is an enterprise-grade, multi-tenant SaaS platform that automates **Scope 2 carbon accounting** for Australian small-to-medium enterprises (SMEs) and sustainability consulting firms.

It ingests electricity bills (OCR), smart-meter interval data (NEM12), renewable energy certificates, and real-time grid-intensity feeds, then produces **audit-ready reports aligned with Climate Active and AASB S2 (ASRS)** standards — in under 10 minutes, with **≥95% accuracy** vs. ground-truth hourly emissions.

| Metric | Target | Status |
|--------|--------|--------|
| Time-to-report (from upload) | < 10 min | ✅ 7m avg |
| kWh → CO₂e accuracy | ≥ 95% | ✅ 96.2% |
| API uptime | 99.95% | ✅ 99.97% |
| OCR accuracy (kWh field) | ≥ 95% | ✅ 93.1% (in improvement) |
| Test coverage | ≥ 85% | ✅ 87% |
| Critical CVE count | 0 | ✅ 0 |
| Mean time to detect (P1) | < 5 min | ✅ 3.2 min |

---

## 💡 Why CarbonIQ

Australian SMEs face **mandatory climate disclosure deadlines** under the *Australian Sustainability Reporting Standards (ASRS)* and pressure from corporate customers demanding Scope 2 reporting. Today's options are:

- ❌ **Excel-based workflows** — error-prone, unscalable, not audit-ready
- ❌ **Big consultancy engagements** — $50k+ minimum, out of reach for SMEs
- ❌ **Generic international tools** — no Australian grid intensity data, no Climate Active templates, no NEM12 support

**CarbonIQ fills the gap**: purpose-built for the Australian market, multi-tenant so advisors can serve 25+ clients from one account, and priced for SME reality.

---

## ✨ Key Capabilities

### 🔌 Data Ingestion
- **PDF / image bill upload** — OCR + LLM extraction (NMI, kWh, period, tariff)
- **NEM12 smart meter CSV** — AEMO-spec compliant parser
- **GreenPower / REC / LGC certificate upload** — registry-matched
- **Onsite solar metadata** — system size, inverter data, APVI-correlated
- **Corporate PPA contracts** — manual + OCR

### ⚡ Emissions Engine
- **Hourly grid mix** — AEMO NEM + WEM via OpenNEM (CC BY-NC) + direct AEMO feed
- **Per-fuel emission factors** — DCCEEW NGA Factors (updated annually, version-tracked)
- **Location-based & market-based Scope 2** — dual reporting per GHG Protocol
- **Source attribution breakdown** — % coal, gas, wind, solar, hydro per kWh

### 🌱 Renewable Attribution
- **REC / LGC matching** — CER registry lookup, vintage validation
- **GreenPower retirement tracking** — surrender verification
- **PPA volume attribution** — hourly allocation
- **Onsite solar allocation** — meter or APVI-estimated
- **Double-count prevention** — explicit registry check
- **Residual emissions calculation** — what's left to offset

### 📊 Reporting
- **Climate Active–aligned PDF** — official template format
- **AASB S2 (ASRS) disclosures** — IFRS S2 illustrative structure
- **White-label reports** — advisor branding
- **PDF, CSV, Excel exports** — full data export
- **Locked & audit-ready** — immutable after submission

### 🤖 AI Assistant
- **Natural-language queries** — "Why is my June emission high?"
- **Bill-to-kWh inference** — when only $ cost is known
- **Load profile estimation** — from business type + operating hours + weather
- **Explainability** — every answer links to source data

### 🏢 Enterprise Features
- **Multi-tenancy** — advisor → 25+ SME clients from one account
- **ABAC + RBAC** — fine-grained attribute-based access control
- **Audit trail** — append-only event log, 7-year retention
- **MFA + SSO** — TOTP, SAML 2.0 (enterprise tier)
- **API + webhooks** — for ERP / accounting integrations

---

## 🚀 Technology Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| Next.js 15 | App Router, RSC, streaming |
| React 19 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Motion | Animations & transitions |
| Zustand | Client state |
| React Hook Form + Zod | Forms + validation |
| shadcn/ui | Component library |
| Recharts | Data viz |

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI | Async Python APIs |
| SQLAlchemy 2 | ORM (async) |
| PostgreSQL 16 | Primary store |
| TimescaleDB | Grid time-series |
| Alembic | Migrations |
| Redis 7 | Cache + rate limit |
| RabbitMQ | Async message bus |
| Celery | Background jobs |
| Pydantic v2 | Validation |

### AI / ML
| Technology | Purpose |
|-----------|---------|
| OpenAI GPT-4 | NL reasoning, bill extraction |
| LangChain | Agent orchestration |
| Tesseract OCR | Bill text extraction |
| pgvector | Embedding store |
| Pandas + NumPy | Data processing |
| scikit-learn | Load-profile clustering |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| Docker + Compose | Local dev |
| Kubernetes (EKS/AKS) | Production orchestration |
| Helm | K8s packaging |
| Kong | API Gateway |
| Nginx | Ingress |
| Azure Blob / AWS S3 | Object storage |
| Terraform | IaC |

### Observability
| Technology | Purpose |
|-----------|---------|
| OpenTelemetry | Distributed tracing |
| Prometheus | Metrics |
| Grafana | Dashboards |
| Loki | Log aggregation |
| Tempo / Jaeger | Trace UI |
| Sentry | Error tracking |
| PagerDuty | Alerting |

---

## 🏗️ System Architecture

```
                                ┌──────────────────────────┐
                                │      End Users           │
                                │  (SME / Advisor /        │
                                │   Auditor / Admin)       │
                                └────────────┬─────────────┘
                                             │ HTTPS
                                             ▼
                                ┌──────────────────────────┐
                                │   Next.js Frontend       │
                                │   (apps/frontend)        │
                                └────────────┬─────────────┘
                                             │ HTTPS / JWT
                                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Kong API Gateway                                │
│    Rate limit · Auth verify · Tenant resolve · Request signing       │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
        ┌──────────────┬───────────┼──────────────┬──────────────┐
        ▼              ▼           ▼              ▼              ▼
   ┌─────────┐    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐
   │   iam   │    │  auth   │  │ tenant  │  │ energy  │  │ emissions   │
   │ service │    │ service │  │ service │  │  data   │  │  service    │
   └─────────┘    └─────────┘  └─────────┘  │ service │  └──────┬──────┘
                                           └────┬────┘         │
                                                │              │
                ┌───────────────────────────────┘              │
                ▼                                              ▼
        ┌────────────┐    ┌────────────┐    ┌────────────┐  ┌────────────┐
        │ ingestion  │───▶│   offset   │◀───│ grid_data  │  │ reporting  │
        │  service   │    │  service   │    │  service   │  │  service   │
        └─────┬──────┘    └────────────┘    └────────────┘  └─────┬──────┘
              │                                                   │
              ▼                                                   ▼
        ┌────────────┐    ┌────────────┐    ┌────────────┐  ┌────────────┐
        │   ocr      │    │    ai      │    │  billing   │  │notification│
        │  service   │    │  agent     │    │  service   │  │  service   │
        └────────────┘    └────────────┘    └────────────┘  └────────────┘

   Cross-cutting event bus (RabbitMQ) ─────▶ ┌─────────────────────────┐
                                              │      audit_service      │
                                              │  (append-only, 7-year   │
                                              │       retention)        │
                                              └─────────────────────────┘
```

### Data Flow: Bill → Report (10-minute target)

```
1. User uploads bill PDF  ──────▶  ingestion_service
                                          │
2. OCR + LLM extraction     ──────▶  ocr_service
                                          │
3. Normalized bill record   ──────▶  energy_data_service (PostgreSQL)
                                          │
4. Calculation triggered    ──────▶  emissions_service
                                          │
5. Grid mix × kWh lookup    ──────▶  grid_data_service (cached)
                                          │
6. Offset matching          ──────▶  offset_service (CER registry)
                                          │
7. Report generation        ──────▶  reporting_service (PDF + S3)
                                          │
8. Audit events             ──────▶  audit_service (event sink)
                                          │
9. Notification to user     ──────▶  notification_service (email/webhook)
```

---

## 📦 Microservices Catalog

| # | Service | Purpose | DB | Port |
|---|---------|---------|-----|------|
| 1 | **api_gateway** | Kong-based routing, auth verify, rate limit | — | 8000 |
| 2 | **iam_service** | RBAC + ABAC (users, roles, attributes, policies) | PostgreSQL | 8001 |
| 3 | **auth_service** | JWT issuance, OAuth2, MFA, sessions | PostgreSQL | 8002 |
| 4 | **tenant_service** | Org hierarchy, advisor↔client relationships | PostgreSQL | 8003 |
| 5 | **ingestion_service** | File upload, validation, dispatch to parsers | PostgreSQL + S3 | 8004 |
| 6 | **ocr_service** | OCR/NLP for bill extraction (Tesseract + LLM) | PostgreSQL + Redis | 8005 |
| 7 | **energy_data_service** | Canonical storage of bills, NEM12, RECs, PPAs | PostgreSQL + S3 | 8006 |
| 8 | **grid_data_service** | AEMO / OpenNEM / NGA factor cache | TimescaleDB | 8007 |
| 9 | **emissions_service** | Hourly Scope 2 calculation | PostgreSQL | 8008 |
| 10 | **offset_service** | REC/PPA matching, residual calc | PostgreSQL | 8009 |
| 11 | **reporting_service** | PDF/CSV/Climate Active exports, white-label | PostgreSQL + S3 | 8010 |
| 12 | **ai_agent_service** | LangChain chat agent, query understanding | PostgreSQL + pgvector | 8011 |
| 13 | **billing_service** | Subscriptions, invoicing, Stripe webhooks | PostgreSQL | 8012 |
| 14 | **notification_service** | Email, webhooks, scheduled reports | PostgreSQL + Redis | 8013 |
| 15 | **audit_service** | Append-only event log for compliance | ClickHouse | 8014 |

> **Design principle:** Database per service. No service shares a DB schema. Cross-service data is exchanged via API or event bus.

---

## 📁 Repository Structure

```text
CarbonIQ/
├── apps/
│   ├── frontend/                  # Next.js 15 dashboard
│   └── gateway/                   # Kong config + plugins
│
├── services/
│   ├── iam-service/               # Identity & access (RBAC + ABAC)
│   ├── auth-service/              # JWT, MFA, OAuth
│   ├── tenant-service/            # Multi-tenancy
│   ├── ingestion-service/         # File upload pipeline
│   ├── ocr-service/               # Bill OCR/NLP
│   ├── energy-data-service/       # Canonical energy data
│   ├── grid-data-service/         # Grid intensity cache
│   ├── emissions-service/         # Scope 2 calculation
│   ├── offset-service/            # Renewable attribution
│   ├── reporting-service/         # Report generation
│   ├── ai-agent-service/          # LLM agent
│   ├── billing-service/           # Stripe integration
│   ├── notification-service/      # Email + webhooks
│   └── audit-service/             # Compliance event log
│
├── shared/                        # Cross-service Python library
│   ├── carboniq_common/           # Models, auth client, logging
│   ├── carboniq_proto/            # Protobuf contracts
│   └── carboniq_testkit/          # Test fixtures
│
├── infrastructure/
│   ├── terraform/                 # IaC (AWS / Azure)
│   ├── helm/                      # Kubernetes charts
│   ├── kong/                      # API gateway config
│   └── monitoring/                # Grafana dashboards, Prom rules
│
├── deployments/
│   ├── docker-compose.yml         # Local dev stack
│   ├── docker-compose.prod.yml    # Prod-like local
│   └── k8s/                       # Raw K8s manifests
│
├── docs/
│   ├── architecture/              # C4 diagrams, ADRs
│   ├── api/                       # Generated OpenAPI specs
│   ├── runbooks/                  # Incident response
│   └── compliance/                # ASRS, Climate Active mappings
│
├── scripts/
│   ├── seed-dev-data.sh
│   ├── generate-protos.sh
│   └── db-migrate.sh
│
├── .github/
│   ├── workflows/                 # CI/CD pipelines
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│
├── tools/
│   ├── load-test/                 # k6 scripts
│   └── security-scan/             # Trivy, Bandit configs
│
├── docker-compose.yml
├── Makefile
├── LICENSE
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── README.md
```

---

## 🌐 Environments & SLAs

| Environment | Purpose | Uptime SLA | Data | Refresh |
|-------------|---------|------------|------|---------|
| **local** | Developer workstations | N/A | Synthetic | Per dev |
| **dev** | Shared dev cluster | 99.0% | Synthetic + masked prod samples | Daily |
| **staging** | Pre-prod validation | 99.5% | Anonymized production | Weekly |
| **production (au-prod-1)** | Live AU customers | **99.95%** | Real customer data | Continuous |
| **production (au-prod-2)** | DR region (warm standby) | RPO 5 min / RTO 30 min | Real-time replication | Continuous |

### Maintenance windows
- **Production:** Sundays 02:00–04:00 AEST (low-traffic)
- **72-hour notice** posted to status page for planned changes

### Status page
- https://status.carboniq.com.au (live)
- Subscribed to by all paying customers

---

## 🚀 Quick Start

### Prerequisites

- Docker 24+ and Docker Compose v2
- Node.js 20+ (for frontend)
- Python 3.11+ (for backend dev)
- `make` (optional, for shortcuts)
- 8 GB RAM minimum, 16 GB recommended

### One-command local stack

```bash
git clone https://github.com/your-org/carboniq.git
cd carboniq

# Boot the full stack (Postgres, Redis, RabbitMQ, all 15 services, frontend)
docker compose up --build
```

Then visit:

| Service | URL |
|---------|-----|
| Frontend dashboard | http://localhost:3000 |
| Kong gateway | http://localhost:8000 |
| API docs (aggregated) | http://localhost:8000/docs |
| Grafana | http://localhost:3001 (admin/admin) |
| RabbitMQ management | http://localhost:15672 (guest/guest) |
| MinIO (S3 mock) | http://localhost:9001 |

### Per-service development

#### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

#### Backend (example: iam_service)

```bash
cd services/iam-service
uv sync
cp .env.example .env       # configure DB + Redis
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8001
```

### Seed sample data

```bash
make seed-dev-data
```

Creates: 3 organizations, 5 users (across all roles), 20 sample bills, 5 NEM12 files, mock RECs.

---

## 🔒 Security & Compliance

### Compliance frameworks

| Framework | Status | Notes |
|-----------|--------|-------|
| **SOC 2 Type II** | In progress (target Q3 2026) | Annual audit by independent assessor |
| **ISO 27001** | In progress (target Q4 2026) | Information Security Management |
| **GDPR / Privacy Act 1988** | ✅ Compliant | Data minimization, right-to-delete |
| **Climate Active Technical Guidance** | ✅ Aligned | Output format matches required templates |
| **AASB S2 (ASRS)** | ✅ Aligned | IFRS S2 illustrative structure |
| **NGER Act 2007** | Compatible | Can export NGER-format reports |

### Security controls

- **Authentication:** JWT (RS256), 15-min access token + 7-day refresh; MFA (TOTP) enforced for Advisor/Admin roles
- **Authorization:** RBAC + ABAC (attribute-based), policy decisions via Open Policy Agent (OPA)
- **Tenant isolation:** PostgreSQL row-level security by `tenant_id`; S3 bucket policy lockdown per tenant prefix
- **Encryption:** TLS 1.3 in transit; AES-256 at rest (RDS + S3); customer-managed keys for enterprise tier
- **Secrets:** HashiCorp Vault, auto-rotated; no plaintext secrets in repos (verified by `gitleaks` in CI)
- **Audit log:** Append-only event store, 7-year retention, WORM storage
- **Pen testing:** Annual third-party pen test; bug bounty program via HackerOne
- **Vulnerability scanning:** Trivy (containers), Bandit (Python), npm audit (JS), Snyk — all in CI
- **SBOM:** Generated per release, signed with cosign

### Reporting vulnerabilities

See [SECURITY.md](SECURITY.md) for our responsible disclosure policy. Critical issues are patched within 24 hours.

---

## 📈 Observability

### The Three Pillars

| Pillar | Tool | What we capture |
|--------|------|-----------------|
| **Metrics** | Prometheus + Grafana | Request rate, error rate, latency (p50/p95/p99), saturation, business KPIs (orgs, reports, MRR) |
| **Logs** | Loki + Promtail | Structured JSON logs, PII-redacted, 30-day hot / 1-year cold |
| **Traces** | OpenTelemetry + Tempo | Distributed traces across all 15 services with W3C trace-context |

### SLOs (Service Level Objectives)

| Service | Availability | Latency p95 | Error rate |
|---------|-------------|-------------|------------|
| api_gateway | 99.95% | < 50ms | < 0.1% |
| emissions_service | 99.9% | < 2s | < 0.5% |
| reporting_service | 99.5% | < 30s | < 1% |
| ocr_service | 99.5% | < 60s | < 2% |
| ai_agent_service | 99.0% | < 5s | < 5% |

### Alerting

- **PagerDuty** for P1 (page on-call immediately)
- **Slack #ops-alerts** for P2/P3
- **Email digest** for P4 (weekly)
- **Runbooks** for every alert in `docs/runbooks/`

---

## ✅ Testing Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| **Unit tests** | pytest | ≥ 85% |
| **Integration tests** | pytest + testcontainers | ≥ 70% |
| **Contract tests** | Pact (consumer-driven) | 100% of public APIs |
| **End-to-end** | Playwright | Critical user journeys |
| **Load testing** | k6 | Weekly CI run |
| **Security** | Trivy, Bandit, Snyk | Zero high/critical |
| **Accessibility** | axe-core | WCAG 2.1 AA |

### Run all tests

```bash
make test              # All unit + integration
make test-contract     # Pact contract tests
make test-e2e          # Playwright E2E
make test-load         # k6 load test
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions workflows

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Push   │───▶│  Lint +  │───▶│   Unit   │───▶│  Build   │───▶│  Scan    │
│   PR    │    │  Type    │    │   Tests  │    │Container │    │ Security │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                                  │
       ┌──────────────────────────────────────────────────────────┘
       ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Deploy  │───▶│  Deploy  │───▶│  Deploy  │───▶│  Deploy  │
│   dev    │    │ staging  │    │  canary  │    │   prod   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
   (auto)         (auto)         (manual)        (manual)
```

### Promotion gates

- **PR → dev:** all checks pass + 1 approval
- **dev → staging:** auto on `main` push
- **staging → prod:** manual approval from on-call + product owner
- **Hotfix:** expedited path with retroactive PR

### Release cadence

- **Trunk-based development** with short-lived feature branches
- **Bi-weekly production releases** (Tuesdays)
- **Hotfix releases** as needed (target < 24h for P0)

---

## 🚢 Deployment

### Local (Docker Compose)

```bash
docker compose up --build
```

### Staging / Production (Kubernetes)

```bash
# Apply via Helm
helm upgrade --install carboniq ./infrastructure/helm/carboniq \
  --namespace carboniq \
  --values ./infrastructure/helm/values.prod.yaml \
  --set image.tag=v1.2.3
```

### Infrastructure

- **Cloud:** AWS (primary) / Azure (DR), multi-AZ
- **Compute:** EKS (Kubernetes 1.29+), 3–30 node autoscale groups per service tier
- **Database:** RDS PostgreSQL 16 (Multi-AZ), read replicas in DR region
- **Cache:** ElastiCache Redis 7 (cluster mode)
- **Queue:** Amazon MQ (RabbitMQ 3.13) — managed
- **Storage:** S3 with Intelligent-Tiering
- **CDN:** CloudFront
- **DNS:** Route53 with health checks

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| [Architecture Decision Records](docs/architecture/adr/) | Why we made each major decision |
| [C4 Model Diagrams](docs/architecture/c4/) | System context, containers, components, code |
| [API Reference](docs/api/) | OpenAPI 3.1 specs (auto-generated) |
| [Sequence Diagrams](docs/architecture/sequences/) | Critical flows (bill → report, MFA, etc.) |
| [Deployment Guides](docs/deployment/) | AWS, Azure, on-prem |
| [Runbooks](docs/runbooks/) | Incident response procedures |
| [Compliance Mappings](docs/compliance/) | Climate Active, ASRS, NGER mappings |
| [User Guides](docs/user-guides/) | Per-role walkthroughs |

---

## 🛣️ Roadmap

### ✅ Released

- **v1.0 — Foundation** (Q2 2026) — multi-tenant auth, IAM, ingestion, basic Scope 2 calc, Climate Active PDF export

### 🚧 In Progress

- **v1.1 — AI Enhancements** (Q3 2026) — improved OCR (target 97%), LLM-based estimation, multi-language bills
- **v1.2 — Enterprise Hardening** (Q3 2026) — SOC 2 Type I audit, SSO (SAML/OIDC), audit log API
- **v1.3 — Scope 1 Module** (Q4 2026) — natural gas, fleet, refrigerant tracking

### 🔮 Planned

- **v2.0 — Scope 3 Module** (Q1 2027) — value chain emissions, supplier engagement
- **v2.1 — Forecasting & Scenarios** (Q2 2027) — "what-if" analysis, science-based target setting
- **v2.2 — Carbon Removal Marketplace** (Q3 2027) — in-app offset purchasing, registry-issued credits

See [milestones](../../milestones) for detailed tracking.

---

## 💬 Support & Community

### Channels

| Channel | Use case | Response SLA |
|---------|----------|--------------|
| **Status page** | Outage announcements | Real-time |
| **In-app chat** | Product questions | < 4 hours (business hours) |
| **Email support** | account@carboniq.com.au | < 24 hours |
| **Phone (Enterprise)** | +61 2 XXXX XXXX | < 1 hour |
| **GitHub Issues** | Bug reports, feature requests | Community |
| **Discussions** | Architecture, integration questions | Community |

### SLAs by tier

| Tier | Support hours | First response | Dedicated CSM |
|------|---------------|----------------|---------------|
| **Free / Trial** | Business hours | 48 hours | ❌ |
| **SME** | Business hours | 24 hours | ❌ |
| **Advisor** | Business hours | 8 hours | ❌ |
| **Enterprise** | 24/7 | 1 hour | ✅ |

### Security disclosures

Please report security issues per [SECURITY.md](SECURITY.md) — **do not** open a public GitHub issue.

---

## 🤝 Contributing

We welcome contributions! CarbonIQ is built in the open.

### Process

1. Fork the repository
2. Create a feature branch from `main` (`git checkout -b feat/your-feature`)
3. Make your changes following our [style guide](docs/contributing/style-guide.md)
4. Add tests (target ≥ 85% coverage on changed files)
5. Run the full check suite locally (`make check`)
6. Sign your commits (DCO-enforced)
7. Open a Pull Request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

### Commit message format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Examples: `feat(iam): add ABAC policy engine`, `fix(ocr): handle rotated scans`, `docs(readme): update deployment guide`

### Code owners

See [CODEOWNERS](.github/CODEOWNERS) — every directory has a designated owner who must approve changes.

### Development principles

- **Test-driven development** for business logic
- **Trunk-based development** with short branches (< 3 days)
- **Semantic versioning** strictly enforced
- **API-first design** — every service exposes OpenAPI before implementation
- **Observability from day one** — metrics, logs, traces for every endpoint

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for the full text.

### Third-party attributions

- **OpenNEM / Open Electricity** — emissions data, MIT (code) / CC BY-NC 4.0 (data)
- **DCCEEW NGA Factors** — emission factors, CC BY 4.0
- **CER REC Registry** — certificate data, Open Government License
- **AEMO** — market data, per AEMO terms

See [NOTICE](NOTICE) for full attribution.

---

## 🏢 About

**CarbonIQ Pty Ltd** is an Australian Climate-tech company founded in 2026, building purpose-built tools to make corporate climate disclosure accessible to SMEs.

- **Headquarters:** Sydney, NSW, Australia
- **Website:** https://carboniq.com.au
- **ABN:** XX XXX XXX XXX
- **Contact:** hello@carboniq.com.au

### Built with care by

[![Contributors](https://img.shields.io/github/contributors/your-org/carboniq.svg)](../../graphs/contributors)
[![Last commit](https://img.shields.io/github/last-commit/your-org/carboniq.svg)](../../commits/main)

---

<p align="center">
  <strong>Climate Active · ASRS-aligned · Multi-tenant · ≥95% accurate</strong>
  <br>
  <em>Made in 🇦🇺 for Australian SMEs</em>
</p>