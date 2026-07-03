# Frontend Static Pages — Implementation TODO

Turns the 42 design mockups in
[`docs/carboniq_decentralized_verification_platform/`](../../docs/carboniq_decentralized_verification_platform/)
into static Next.js routes under `src/app/`. "Static" means UI/markup + placeholder
data only — no live API wiring, since the backend services aren't implemented yet
(see root `CLAUDE.md`). Each mockup folder has `code.html` (source markup/Tailwind
classes to port) and `screen.png` (visual reference). Design tokens (colors,
type scale, spacing, elevation) come from
[`docs/.../carboniq/DESIGN.md`](../../docs/carboniq_decentralized_verification_platform/carboniq/DESIGN.md) —
match it exactly rather than inventing new values.

Three phases, ordered by dependency: **design system → core product → ecosystem/admin**.
Nothing in Phase 2 or 3 should be started before the shell it depends on exists —
build shells before the pages that live inside them.

---

## Phase 1 — Design System, Marketing & Onboarding Funnel ✅ done

**Why first:** everything else reuses these primitives, and these routes are all
public/unauthenticated, so they carry no data-modeling risk. Order follows the
actual signup funnel (browse → learn → price → sign up → pay → onboard) so each
step's UI naturally leads into the next.

- [x] 1. **Design system & primitives** — source: `carboniq_ui_components_library`.
      No route. Built `src/components/ui/` (Button, GlassCard, StatusBadge, Input/
      Textarea/Select, SegmentedControl, MetricCircle, Logo) and wired the full
      EcoLens/CarbonIQ token set into `src/app/globals.css` via Tailwind v4's
      `@theme` (colors, Geist/Inter font pairings, type scale, spacing, the
      `glass-card`/`neon-glow`/`status-badge` recipes). Everything below consumes
      this. Visual QA: see `/preview`.
- [x] 2. **Brand mark** — source: `carboniq_hexagonal_logo`. No route. Extracted
      into `public/logo.svg` and `src/components/ui/Logo.tsx` for use in nav/headers.
- [x] 3. **Landing page** — `/` ← `carboniq_landing_page`
- [x] 4. **About** — `/about` ← `about_carboniq_mission_vision`
- [x] 5. **Methodology** — `/methodology` ← `carboniq_methodology_protocol_standards`
- [x] 6. **Protocol specifications** — `/protocol/specifications` ← `carboniq_protocol_specifications`
      (own topbar+sidebar chrome, distinct from the marketing header, matching the mockup)
- [x] 7. **Developer docs hub** — `/docs` ← `technical_documentation_hub`
      (own topbar+sidebar chrome; code-language tabs are a client component)
- [x] 8. **Journey to Credit (interactive guide)** — `/journey-to-credit` ← `journey_to_credit_interactive_guide`
- [x] 9. **Pricing** — `/pricing` ← `subscription_pricing_tiers` (monthly/annual
      billing toggle is a client component)
- [x] 10. **Auth (login/signup)** — `/login`, `/signup` ← `authentication_portal`
      (shared `AuthCard` client component, tab defaults to sign-in vs. sign-up per route)
- [x] 11. **Checkout** — `/checkout` ← `payment_checkout_flow` (crypto/fiat
      payment-method tabs are a client component)
- [x] 12. **Tenant onboarding** — `/onboarding` ← `tenant_onboarding_setup`

Not done in this pass (left for later, out of scope for a static port): real
form validation/submission, wallet connect, and the mouse-follow glow
micro-interactions some mockups had in vanilla JS.

---

## Phase 2 — Core Authenticated Product (EcoLens Dashboard) ✅ done

**Why second:** this is the MVP feature set from the root `README.md` (ingestion →
normalization → Scope 2 calculation → attribution → reporting → notifications).
All of it lives behind the app shell, so build the shell once and reuse it for
every page below rather than re-deriving the sidebar/topbar per page.

- [x] 1. **App shell layout** — source: `carboniq_dashboard` (chrome only: fixed
      256px sidebar, topbar, 1280px content well). Built `src/app/(app)/layout.tsx`
      with `src/components/app/Sidebar.tsx` (client, highlights active route via
      `usePathname`) and `Topbar.tsx`; every route below renders inside it. Sidebar
      nav consolidates all Phase 2 destinations into one flat list rather than
      re-deriving a different nav per mockup.
- [x] 2. **Dashboard home** — `/dashboard` ← `carboniq_dashboard` (content)
- [x] 3. **Dashboard lens view** — `/dashboard/lens` ← `ecolens_core_dashboard_lens_view`
- [x] 4. **Granular impact dashboard** — `/dashboard/impact` ← `ecolens_granular_impact_dashboard`
- [x] 5. **Data ingestion hub** — `/ingestion` ← `emissions_data_ingestion_hub` — **later wired live** to `services/ingestion-service` (see Post-Phase-3 note below); no longer static placeholder data
- [x] 6. **Data integration & sources hub** — `/integrations` ← `ecolens_data_integration_sources_hub`
- [x] 7. **Data health & lineage monitor** — `/data-health` ← `ecolens_data_health_lineage_monitor`
      (this mockup and `/integrations` overlap heavily in the source material —
      kept `/integrations` focused on gateways/API keys/connectivity, `/data-health`
      focused on confidence scoring/lineage, per the two mockups' distinct framing)
- [x] 8. **AI estimation & load profiling** — `/ai-estimation` ← `ai_estimation_load_profiling`
- [x] 9. **Scope 2 inventory & analysis** — `/scope-2` ← `scope_2_inventory_analysis`
- [x] 10. **Renewables attribution manager** — `/renewables-attribution` ← `renewables_attribution_manager`
- [x] 11. **Compliance & policy engine** — `/compliance/policy-engine` ← `ecolens_compliance_policy_engine_1` + `ecolens_compliance_policy_engine_2` (merged: threshold sliders/simulation from variant 1, verification-frequency toggle from variant 2)
- [x] 12. **Compliance reporting center** — `/compliance/reports` ← `compliance_reporting_center_1` + `compliance_reporting_center_2` (merged: framework selector/alignment/AI gaps from variant 1, readiness validator/historical ledger from variant 2)
- [x] 13. **Analytics & reporting deep dive** — `/analytics` ← `ecolens_analytics_reporting_deep_dive_1` + `ecolens_analytics_reporting_deep_dive_2` (variant 2 was the more complete mockup; used it as the primary source)
- [x] 14. **Notifications & alerts center** — `/notifications` ← `notifications_alerts_center` (alert-preference toggles are a client component)

New shared components added along the way: `src/components/ui/Sparkline.tsx`
(reusable SVG line/area chart for the dashboard, AI estimation, scope-2, and
analytics pages). Charts and tables everywhere use static placeholder data —
no live data wiring, per the "static pages" scope of this whole TODO — **except**
`/ingestion`, wired live after Phase 3 (see below).

---

## Post-Phase-3 — `/ingestion` wired to `services/ingestion-service`

Once `services/ingestion-service` (FastAPI + Celery + uv) became real, working
code, `/ingestion` was rebuilt to actually call it instead of rendering
hardcoded arrays — the first (and so far only) page that isn't purely static.

- `src/lib/ingestion/` — server-only: JWT minting (`auth.ts`, demo HS256 token
  until `auth-service` exists), a typed fetch client (`client.ts`), and shared
  types mirroring the backend's Pydantic schemas (`types.ts`).
- `src/app/api/ingestion/uploads/**` — Next.js Route Handlers that proxy to
  ingestion-service server-side (BFF pattern) — the browser never sees the
  backend URL or the JWT secret, and there's no CORS to configure since it's
  server-to-server.
- `src/app/(app)/ingestion/IngestionDashboard.tsx` — client component: real
  file upload (with an explicit Data Type selector, since the backend can't
  infer `bill_pdf` vs `rec_certificate` from content alone), polls for status
  changes while anything is non-terminal, and renders Active/Recent sections
  from live data. The AI Insights / Compliance Guard side panels stay static
  — there's no `ai-agent-service` yet to back them.
- Requires `apps/frontend/.env.local` (see `.env.example`) plus
  `services/ingestion-service` actually running (Postgres/RabbitMQ/Redis/MinIO
  + `uv run uvicorn` + `uv run celery worker`) for the page to do anything.
  Without it, the page loads and shows a clear "service unreachable" error
  banner rather than crashing.

---

## Phase 3 — Verification Ecosystem & Platform Administration ✅ done

**Why last:** these screens are specialized (decentralized-verification/protocol
mechanics, or admin-only platform ops) rather than daily-use SME flows, and several
visually imply their own shell variant (`CarbonIQ Protocol` chrome for 3A,
`EcoAdmin` chrome for 3B) — confirm/build those shells before their child pages.

### 3A — Verification, Credits & Protocol Ecosystem

- [x] 1. **Project verification portal** — `/verification/projects` ← `project_verification_portal_1` + `project_verification_portal_2` (variant 1's evidence grid/auditor panel/issuance card used as primary source; variant 2's 4-step stepper visual kept)
- [x] 2. **Evidence verification timeline** — `/verification/evidence` ← `evidence_verification_timeline`
- [x] 3. **Credit lifecycle explorer** — `/credits/lifecycle` ← `credit_lifecycle_explorer`
- [x] 4. **Credit marketplace** — `/marketplace` ← `carboniq_credit_marketplace` (secondary filter sidebar rendered inside the main `(app)` shell rather than as the primary nav)
- [x] 5. **Smart contract registry** — `/protocol/smart-contracts` ← `smart_contract_registry`
- [x] 6. **Node status & network health** — `/protocol/nodes` ← `node_status_network_health`
- [x] 7. **Governance portal** — `/governance` ← `governance_portal` (source mockup's sidebar was a mismatched copy-paste from the docs hub mockup, so this uses the standard `(app)` shell instead)

Items 1–4 and 7 live under the main `(app)` shell (`src/components/app/Sidebar.tsx`,
now with an added "Ecosystem" nav group: Verification, Marketplace, Credit
Lifecycle, Governance). Items 5–6 use a new shared
`src/components/protocol/ProtocolSidebar.tsx` ("CarbonIQ Protocol" chrome:
Dashboard/Protocols/Verification/Registry/Analytics), matching
`/protocol/specifications` from Phase 1 — that page wasn't refactored to use
the shared component to avoid touching already-working code, but any new
Protocol page should use `ProtocolSidebar`.

### 3B — Admin & Platform Operations (EcoAdmin) ✅ done

- [x] 8. **Admin / IAM control center** — `/admin` ← `admin_iam_control_center_1` + `admin_iam_control_center_2` (merged: metrics/org table/security toggles from variant 1, activity feed/compliance ring from variant 1; tenant cards style from variant 2 folded into the org table)
- [x] 9. **Users & roles management** — `/admin/users-roles` ← `users_roles_management`
- [x] 10. **API & security console** — `/admin/api-security` ← `api_security_controls`
- [x] 11. **System settings / microservice config** — `/admin/settings` ← `ecolens_system_settings_api_config_1` + `ecolens_system_settings_api_config_2` (both source mockups actually used the regular EcoLens dashboard nav, not EcoAdmin — placed under `/admin/settings` anyway since it's conceptually an admin function, using the `AdminSidebar` for consistency)
- [x] 12. **System audit logs** — `/admin/audit-logs` ← `system_audit_logs`

New shared shell: `src/components/admin/AdminSidebar.tsx` +
`AdminTopbar.tsx`, wired up in `src/app/admin/layout.tsx` (nav: Organization,
Users & Roles, API & Security, Settings, Audit Logs) — every `/admin/*` route
renders inside it, same one-shell-many-pages pattern as Phase 2's `(app)` shell.

No new reusable `src/components/ui/*` primitives were needed for Phase 3 — all
pages compose the existing `GlassCard`, `StatusBadge`, `Sparkline`, `Button`,
`Input` set from `/preview`, so that gallery didn't need updates.

---

## Notes

- Where two mockups map to one page (`_1`/`_2` suffixes), treat the pair as
  alternate explorations of the same screen — reconcile them into a single
  implementation rather than shipping both.
- Route paths above are suggestions, not mandates — adjust to taste, but keep
  Phase 1 outside any authenticated route group, Phase 2 under one `(app)` shell,
  and Phase 3B under its own `(admin)` shell to match the distinct chrome implied
  by the mockups.
- Once real backend services exist (see `services/*`), a later pass wires these
  static pages to live data — out of scope for this TODO.
