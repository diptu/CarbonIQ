# Emissions Service

Status: planned — not yet implemented.

Computes hourly Scope 2 emissions (kWh × hourly/regional grid intensity), combining canonical consumption data from the [energy-data-service](../energy-data-service/README.md) with grid mix/factor data from the [grid-data-service](../grid-data-service/README.md). Supports both location-based and market-based methods per the GHG Protocol.

- **Database:** PostgreSQL
- **Port:** 8008

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture.
