# Scripts

Developer and operations scripts.

- **[synthictic_bill_generator.py](synthictic_bill_generator.py)** — implemented. Generates synthetic Australian energy bills (AGL/Origin/EnergyAustralia/RedEnergy/Alinta/Synergy-styled PDFs, with optional scan/photo/fax quality degradation) plus ground-truth `metadata.json`, for OCR pipeline testing. Run `python synthictic_bill_generator.py --output ./synthetic_bills --count 50`.
- **[seed-dev-data.sh](seed-dev-data.sh)** — planned. Seeds the local dev stack (orgs, users, bills, NEM12 files, mock RECs).
- **[generate-protos.sh](generate-protos.sh)** — planned. Compiles `shared/carboniq_proto/` contracts.
- **[db-migrate.sh](db-migrate.sh)** — planned. Runs Alembic migrations across all services.

See the root [README.md](../README.md) for how this fits into the overall CarbonIQ architecture.
