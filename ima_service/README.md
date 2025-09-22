# IMA Service

FastAPI auth/RBAC microservice with JWT (access/refresh), Redis-backed refresh rotation, tenant isolation, and a simple Users API.

## Endpoints
- `GET  /api/v1/health`
- `POST /api/v1/auth/login` (OAuth2 form: `username`, `password`, optional `X-Tenant-ID`)
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout` (body: `{"refresh_token": "...", "all": false}`)
- `GET  /api/v1/users/me` (requires Bearer; honors `X-Tenant-ID`)
- `GET  /api/v1/users` (Owner)
- `POST /api/v1/users` (Owner)
- `DELETE /api/v1/users/{id}` (Owner)

## Quick start (dev)
```bash
# deps
uv sync --dev

# infra (redis + postgres)
docker compose -f infra/docker-compose.yml up -d

# run
uv run uvicorn main:app --reload --port 8000
```

## ENV examples
export IMA_APP_NAME="IMA Service"
export IMA_ENV="dev"
export IMA_JWT__SECRET_KEY="change-me"
export IMA_REDIS_DSN="redis://localhost:6379/0"
# DB (optional; SQLModel repo)
```bash
export IMA_DB__URL="postgresql+psycopg://postgres:postgres@localhost:5432/ima"
```
## Curl examples
```bash
# login (demo bootstrap user)
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-Tenant-ID: acme' \
  -d 'username=admin@example.com&password=secret' | jq

# me
ACCESS=...  # from login
curl -sS http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer $ACCESS" \
  -H "X-Tenant-ID: acme" | jq

# refresh
REFRESH=...
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}" | jq

# logout (single)
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/logout \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}" -i

# create user (Owner only)
curl -sS -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer $ACCESS" -H "X-Tenant-ID: acme" \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@acme.io","password":"p@55w0rd","role":"viewer"}' | jq

```

## Code structure
```bash
app/
  core/         # settings, security(JWT+deps), logging, errors, token_store
  api/v1/       # health, auth, users/* + routes aggregator
  domain/       # schemas/models/services (repo-agnostic, in-mem fallback)
  persistence/  # db engine + SQLModel repo (optional)

```