#!/usr/bin/env bash
# Minimal, production-ready entrypoint: optional migrations → uvicorn.
set -Eeuo pipefail

: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"
: "${UVICORN_WORKERS:=1}"
: "${RUN_MIGRATIONS:=1}"

echo "Starting IMA service on ${HOST}:${PORT} (workers=${UVICORN_WORKERS})"

# Run Alembic migrations if configured
if [[ "${RUN_MIGRATIONS}" == "1" && -f "alembic.ini" ]]; then
  echo "Applying migrations (alembic upgrade head)…"
  if ! alembic -c alembic.ini upgrade head; then
    echo "WARN: Alembic failed or not configured; continuing startup." >&2
  fi
fi

# Launch app
exec uvicorn main:app --host "${HOST}" --port "${PORT}" --workers "${UVICORN_WORKERS}"
