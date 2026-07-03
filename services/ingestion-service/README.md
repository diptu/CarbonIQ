# Ingestion Service

Status: **implemented** (FastAPI + Celery + uv). Handles file upload and structural validation (PDF/image bills, NEM12 smart-meter CSVs, REC/LGC certificates, PPA contracts), then dispatches validated files downstream (`ocr-service`, `energy-data-service`, or `offset-service`, depending on file type).

- **Database:** PostgreSQL
- **Object storage:** S3-compatible (MinIO locally)
- **Port:** 8004

See the root [README.md](../../README.md) for how this service fits into the overall CarbonIQ architecture, and [CLAUDE.md](../../CLAUDE.md) for the repo-wide auth/tenancy model this service implements against.

## Architecture

```
POST /api/v1/uploads
        │
        ▼
  validate size/type, compute checksum, write to S3, insert DB row (status=pending)
        │
        ▼
  enqueue validate_file_task (Celery, queue "ingestion")
        │
        ▼
  structural validation (magic bytes / NEM12 record framing / content-type)
        │
   ┌────┴────┐
   ▼         ▼
VALIDATED  VALIDATION_FAILED (terminal)
   │
   ▼
enqueue dispatch_file_task → POST to the downstream service's /api/v1/intake
   │
   ┌────┴──────┐
   ▼           ▼
DISPATCHED   DISPATCH_FAILED (retried up to 5x, exponential backoff)
```

Every `/api/v1/*` route (except `/healthz`) requires a JWT issued by `auth-service`, and every query is scoped to the caller's `tenant_id` claim — deny-by-default, per the repo's zero-trust model. Responses follow the standard envelope: `{"success": bool, "data": ..., "meta": {"request_id", "timestamp"}}` on success, `{"success": false, "error": {"code", "message"}, "meta": {...}}` on failure.

## Local development

### Prerequisites

Postgres, RabbitMQ, Redis, and an S3-compatible store (MinIO) — either run these yourself, or use the root [Quick Start](../../README.md#-quick-start)'s `docker compose up` once `deployments/docker-compose.yml` is implemented. For now, the fastest way to get all four locally:

```bash
docker run -d -p 5432:5432 -e POSTGRES_USER=carboniq -e POSTGRES_PASSWORD=carboniq -e POSTGRES_DB=ingestion postgres:16-alpine
docker run -d -p 5672:5672 rabbitmq:3-management-alpine
docker run -d -p 6379:6379 redis:7-alpine
docker run -d -p 9000:9000 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin minio/minio server /data
```

### Run the API

```bash
cd services/ingestion-service
uv sync
cp .env.example .env       # adjust DATABASE_URL / broker / S3 creds as needed
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8004
```

API docs at `http://localhost:8004/docs`.

### Run the Celery worker (separate terminal)

```bash
cd services/ingestion-service
uv run celery -A app.celery_app worker --loglevel=info
```

### Auth in local dev

Without a running `auth-service`, set `JWT_ALGORITHM=HS256` and `JWT_HS256_SECRET` in `.env`, then mint a token for testing:

```bash
uv run python -c "
import jwt, datetime
print(jwt.encode({
    'sub': 'u_test', 'tenant_id': 't_test', 'roles': ['tenant_admin'],
    'permissions': [], 'iss': 'auth.service.local',
    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
}, 'local-dev-shared-secret', algorithm='HS256'))
"
```

Use it as `Authorization: Bearer <token>`.

### Tests

```bash
uv run pytest
```

The suite runs against an in-memory SQLite database and a fake object store — no external services required. `tests/test_ingestion_tasks.py` exercises the validate → dispatch pipeline directly (bypassing Celery's broker); `tests/test_uploads_api.py` covers the HTTP API, auth, and tenant isolation.

### Lint

```bash
uv run ruff check .
```

## API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/uploads` | Upload a file (`multipart/form-data`: `file`, `file_type`) | ✅ |
| GET | `/api/v1/uploads` | List uploads for the caller's tenant (paginated, filterable by `file_type`/`upload_status`) | ✅ |
| GET | `/api/v1/uploads/{id}` | Get a single upload's status | ✅ |
| GET | `/api/v1/uploads/{id}/download-url` | Presigned S3 URL for the original file | ✅ |
| DELETE | `/api/v1/uploads/{id}` | Delete an upload (storage + record) | ✅ |
| GET | `/healthz` | Liveness + DB connectivity check | ❌ |

`file_type` is one of: `bill_pdf`, `bill_image`, `nem12_csv`, `rec_certificate`, `lgc_certificate`, `ppa_contract`.

## Project layout

```
app/
├── main.py                FastAPI app factory
├── config.py               Pydantic Settings (env-driven)
├── db.py                   Async SQLAlchemy engine/session
├── celery_app.py           Celery app (RabbitMQ broker, Redis backend)
├── core/
│   ├── security.py         JWT verification + AuthContext (tenant/RBAC)
│   ├── responses.py        Success/error envelope helpers
│   └── exceptions.py       Exception handlers → envelope errors
├── models/ingested_file.py SQLAlchemy model (tenant-scoped)
├── schemas/ingested_file.py Pydantic request/response schemas
├── storage/s3.py            boto3/S3 wrapper (MinIO-compatible)
├── validators/              Per-file-type structural validation
├── tasks/ingestion_tasks.py Celery tasks: validate_file_task, dispatch_file_task
└── api/v1/                  Routes: uploads, health
migrations/                  Alembic (async env.py, autogenerate-ready)
tests/                       pytest + pytest-asyncio, no external services needed
```
