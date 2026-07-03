# Tools

Status: planned — not yet implemented.

Operational tooling separate from the application code:

- **[load-test/](load-test/)** — k6 scripts for load/performance testing the API gateway and services.
- **[security-scan/](security-scan/)** — Trivy (containers) and Bandit (Python) configs for security scanning, run in CI.

See the root [README.md](../README.md) for how this fits into the overall CarbonIQ architecture.
