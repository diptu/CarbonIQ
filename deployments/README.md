# Deployments

Status: planned — not yet implemented.

Environment-specific deployment configuration:

- **[docker-compose.yml](docker-compose.yml)** — full local dev stack (Postgres, TimescaleDB, Redis, RabbitMQ, ClickHouse, MinIO, all services, frontend).
- **[docker-compose.prod.yml](docker-compose.prod.yml)** — prod-like local stack for pre-deploy verification.
- **[k8s/](k8s/)** — raw Kubernetes manifests.

See the root [README.md](../README.md) for how this fits into the overall CarbonIQ architecture.
