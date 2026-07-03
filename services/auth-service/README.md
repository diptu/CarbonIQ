# Auth Service

Status: planned — not yet implemented.

Issues and verifies JWTs (RS256, 15-min access + 7-day refresh), OAuth2 flows, MFA (TOTP), and session management. Distinct from [iam-service](../iam-service/README.md), which owns users/roles/permissions/policies — auth-service is the token/session layer in front of it.

- **Database:** PostgreSQL
- **Port:** 8002

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture.
