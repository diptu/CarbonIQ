# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This repo is a **mix of real, working code and planning scaffolding**. Don't assume uniformly — check each area:

- **`apps/frontend/`** — real, working Next.js 15 + TypeScript app. All 3 implementation phases from `apps/frontend/todo.md` are complete: 37 routes covering the marketing/onboarding funnel, the EcoLens SaaS dashboard, and the verification/admin ecosystem. Static UI only (placeholder data, no live API wiring) — see `apps/frontend/CLAUDE.md` / `AGENTS.md` for frontend-specific conventions. Has a real build/lint/dev toolchain (`npm run build`, `npm run lint`, `npm run dev`).
- **`services/*`** — planning only. Every service directory holds a one-line placeholder `README.md` ("planned — not yet implemented"), **except** `services/iam-service/` and `services/tenant-service/`, which have real planning content (auth/tenancy model, API shapes — see below). Don't infer implementation details from the placeholders; they exist purely to keep the tree matching the README's Microservices Catalog.
- **`scripts/synthictic_bill_generator.py`** — real, working Python script (generates synthetic Australian energy bills for OCR testing). Everything else under `scripts/` is a placeholder stub.
- Everything else (`infrastructure/`, `deployments/`, `shared/`, `tools/`, `.github/`, root `docker-compose.yml`/`Makefile`) is placeholder-only.

The top-level layout mirrors the "Repository Structure" section of `README.md`:

```text
CarbonIQ/
├── apps/
│   ├── frontend/          real Next.js 15 dashboard (37 routes, Phases 1-3 done)
│   └── gateway/           planned Kong API Gateway config
├── services/               (14 services; see Microservices Catalog in README.md)
│   ├── iam-service/         real planning docs (README.md, example_api.md)
│   ├── auth-service/        placeholder only
│   ├── tenant-service/      real planning docs (README.md, example_api.md)
│   ├── ingestion-service/   placeholder only
│   ├── ocr-service/         placeholder only
│   ├── energy-data-service/ placeholder only
│   ├── grid-data-service/   placeholder only
│   ├── emissions-service/   placeholder only
│   ├── offset-service/      placeholder only
│   ├── reporting-service/   placeholder only
│   ├── ai-agent-service/    placeholder only
│   ├── billing-service/     placeholder only
│   ├── notification-service/ placeholder only
│   └── audit-service/       placeholder only
├── shared/                carboniq_common/, carboniq_proto/, carboniq_testkit/ (all placeholder)
├── infrastructure/        terraform/, helm/, kong/, monitoring/ (all placeholder)
├── deployments/           docker-compose.yml, docker-compose.prod.yml, k8s/ (all placeholder)
├── docs/                  design mockups + design system (real, see below) +
│                          architecture/, api/, runbooks/, compliance/, deployment/,
│                          user-guides/, contributing/ (all placeholder)
├── scripts/               synthictic_bill_generator.py (real) + 3 placeholder stubs
├── tools/                 load-test/, security-scan/ (all placeholder)
├── .github/               workflows/, CODEOWNERS, PULL_REQUEST_TEMPLATE.md,
│                          ISSUE_TEMPLATE/ (all placeholder)
├── docker-compose.yml     placeholder (commented stub)
├── Makefile               placeholder (commented stub)
├── CHANGELOG.md, CODE_OF_CONDUCT.md, SECURITY.md, NOTICE   placeholder
└── README.md
```

Because backend code doesn't exist yet, there are no backend lint/build/test commands to run. For the frontend, `cd apps/frontend` and use `npm run build` / `npm run lint` / `npm run dev` — see `apps/frontend/CLAUDE.md` for details. When backend implementation begins, update this file with the actual commands.

## Target architecture (per README.md and service docs — mostly not yet built)

CarbonIQ is planned as a multi-tenant SaaS platform for automated Scope 2 carbon accounting (Climate Active / ASRS-aligned reporting for Australian SMEs). Planned stack:

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, Motion, Zustand, React Hook Form + Zod, shadcn/ui, Recharts — **the frontend app itself is built**; the state-management/forms/charts libraries beyond what's already in `apps/frontend/package.json` are not yet wired in since all pages are still static.
- **Backend:** FastAPI, SQLAlchemy 2 (async), PostgreSQL 16, TimescaleDB, Alembic, Redis, RabbitMQ, Celery, Pydantic v2
- **AI/ML:** OpenAI GPT-4, LangChain, Tesseract OCR, pgvector, Pandas, NumPy, scikit-learn
- **Infra:** Docker Compose, Kubernetes (EKS/AKS), Helm, Kong API Gateway, Nginx, Azure Blob / AWS S3, Terraform
- **Observability:** OpenTelemetry, Prometheus, Grafana, Loki, Tempo/Jaeger, Sentry, PagerDuty

Planned microservices (14, plus the Kong `api_gateway` under `apps/gateway`) — see README.md's Microservices Catalog table for the full purpose/DB/port breakdown per service:

`iam` → `auth` → `tenant` → `ingestion` → `ocr` → `energy_data` → `grid_data` → `emissions` → `offset` → `reporting` → `ai_agent` → `billing` → `notification`, plus `audit` as a cross-cutting sink off the RabbitMQ event bus. Each service is tenant-scoped, enforces RBAC via JWT claims issued by `auth-service`, and owns its own database (database-per-service — no shared schemas).

### Auth/tenancy model (from `services/iam-service/README.md` and `services/tenant-service/README.md`)

- **Hierarchy:** Organization → Tenant → Subtenant (optional) → User.
- **iam-service** owns RBAC + ABAC: `users`, `roles`, `permissions`, `role_permissions`, `user_roles`, policies, audit logs. **auth-service** (separate from iam-service per the current README) is the token/session layer: JWT issuance (RS256, 15-min access + 7-day refresh), OAuth2, MFA (TOTP), sessions.
- **tenant-service** owns `organizations`, `tenants`, `tenant_users`, resolves tenant by subdomain (e.g. `acme.carboniq.ai` → `tenant_id`), and enforces tenant scoping; it trusts JWTs issued by auth-service rather than performing auth itself.
- JWTs carry `sub`, `tenant_id`, `roles`, `permissions`, `exp`, `iss` claims. Every downstream service is expected to validate the JWT and apply tenant + RBAC filtering — deny-by-default (zero-trust), not tenant-optional.
- API responses follow a consistent envelope: `{"success": bool, "data": ..., "meta": {"request_id", "timestamp"}}` on success, `{"success": false, "error": {"code", "message"}, "meta": {...}}` on failure. Match this envelope when implementing new endpoints — see `services/iam-service/example_api.md` and `services/tenant-service/example_api.md` for full request/response examples per endpoint.

## Frontend (`apps/frontend/`)

Next.js 15 App Router + TypeScript + Tailwind CSS v4 (CSS-first `@theme` config, not `tailwind.config.js`). Two chrome patterns: the `(app)` route group (`src/components/app/Sidebar.tsx` + `Topbar.tsx`) for the main EcoLens dashboard, and dedicated shells for `/protocol/*` (`ProtocolSidebar`) and `/admin/*` (`AdminSidebar`/`AdminTopbar`) sections. Design tokens and component conventions are documented in `apps/frontend/todo.md` (implementation plan + notes) and the design system reference under `docs/.../DESIGN.md` (see below). All pages are static — UI/markup + placeholder data, no live backend wiring, since the services above don't exist yet.

## Design system (`docs/.../carboniq/DESIGN.md`)

Brand: "EcoLens" — a dark, high-precision "Cyber-Glassmorphism" dashboard aesthetic for sustainability/systems engineers.

- **Surfaces:** deep "Forest Black" (`#0C150F`) base, never solid black; layered `glass-card` containers (`background: rgba(6,44,34,0.6); backdrop-filter: blur(16px)`) with 10% white borders.
- **Primary accent:** Neon Mint `#00FF9D` (critical data, success, primary actions, often with an outer glow). **Secondary:** `#00D1FF` for auxiliary data streams.
- **Typography:** dual-font — **Geist** for headlines/labels/numeric data, **Inter** for body text. Metadata/category labels are uppercase with +5% letter spacing.
- **Layout:** fixed 256px sidebar, fluid main content capped at 1280px, 12-column grid, 4px base spacing unit, 64px desktop margins.
- **Depth:** built via blur + luminance ("Active Glow" box-shadows), not black drop shadows.
- **Shape:** 8px base radius for standard components, 12px for larger widgets, full/pill radius for search bars and segmented toggles.

When creating or editing a mockup under `docs/.../<screen_name>/code.html`, match this system exactly (reuse the same Tailwind config/CSS custom properties already present in sibling `code.html` files) rather than inventing new tokens. When building real pages in `apps/frontend/`, remember Tailwind v4's static scanner does **not** pick up dynamic template-literal class names (e.g. `` `bg-${var}/20` ``) — use static class strings or lookup objects instead.
