# OCR Service

Status: planned — not yet implemented.

Extracts structured fields (NMI, kWh, billing period, tariff) from uploaded bill PDFs/images using Tesseract OCR + LLM-assisted extraction. Consumes files staged by the [ingestion-service](../ingestion-service/README.md) and writes normalized records to the [energy-data-service](../energy-data-service/README.md).

- **Database:** PostgreSQL + Redis
- **Port:** 8005

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture.
