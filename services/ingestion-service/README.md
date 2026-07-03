# Ingestion Service

Status: planned — not yet implemented.

Handles file upload and validation (PDF/image bills, NEM12 smart-meter CSVs, REC/LGC certificates, PPA contracts), then dispatches to the [ocr-service](../ocr-service/README.md) or the appropriate parser.

- **Database:** PostgreSQL + S3
- **Port:** 8004

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture.
