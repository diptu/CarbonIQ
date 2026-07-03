# Energy Data Service

Status: planned — not yet implemented.

Canonical storage for all energy data: OCR'd bills, NEM12 smart-meter interval data, RECs/LGCs, and PPA contracts. The single source of truth consumed by [emissions-service](../emissions-service/README.md) and [offset-service](../offset-service/README.md).

- **Database:** PostgreSQL + S3
- **Port:** 8006

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture.
