# Infrastructure

Status: planned — not yet implemented.

Shared infrastructure config, split by concern:

- **[terraform/](terraform/)** — IaC for AWS/Azure (VPC, RDS, EKS/AKS, S3/Blob storage).
- **[helm/](helm/)** — Kubernetes charts for packaging each service under `services/`.
- **[kong/](kong/)** — API Gateway config: routing, JWT verification, rate limiting.
- **[monitoring/](monitoring/)** — Grafana dashboards and Prometheus alerting rules.

See the root [README.md](../README.md) for how this fits into the overall CarbonIQ architecture.
