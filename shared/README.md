# Shared

Status: planned — not yet implemented.

Cross-service Python library, installed as a dependency by every service under `services/`:

- **[carboniq_common/](carboniq_common/)** — shared models, the auth client (JWT verification against `auth-service`), and structured logging setup.
- **[carboniq_proto/](carboniq_proto/)** — protobuf contracts for inter-service messages (RabbitMQ event bus payloads).
- **[carboniq_testkit/](carboniq_testkit/)** — shared pytest fixtures (test DB, mock tenant/user factories) for service test suites.

See the root [README.md](../README.md) for how this fits into the overall CarbonIQ architecture.
