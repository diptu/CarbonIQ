#!/usr/bin/env bash
# Wait for Postgres to be ready.
# Usage: HOST=localhost PORT=5432 ./wait_for_db.sh
set -Eeuo pipefail

cd "$(dirname "$0")/.."

HOST="${HOST:-}"
PORT="${PORT:-}"

# Try to infer from DSN (IMA_DB__URL=postgresql+psycopg://u:p@h:5432/db)
if [[ -z "$HOST" || -z "$PORT" ]] && [[ -n "${IMA_DB__URL:-}" ]]; then
  # shellcheck disable=SC2001
  HOST="$(echo "$IMA_DB__URL" | sed -E 's#.*@([^:/]+):?([0-9]*)/.*#\1#')"
  PORT="$(echo "$IMA_DB__URL" | sed -E 's#.*@([^:/]+):?([0-9]*)/.*#\2#')"
fi

HOST="${HOST:-localhost}"
PORT="${PORT:-5432}"

echo "Waiting for postgres at $HOST:$PORT ..."

if command -v pg_isready >/dev/null 2>&1; then
  until pg_isready -h "$HOST" -p "$PORT" >/dev/null 2>&1; do sleep 1; done
  echo "Postgres is ready."; exit 0
fi

if command -v nc >/dev/null 2>&1; then
  until nc -z "$HOST" "$PORT" >/dev/null 2>&1; do sleep 1; done
  echo "Postgres is ready."; exit 0
fi

until (echo >"/dev/tcp/$HOST/$PORT") >/dev/null 2>&1; do sleep 1; done
echo "Postgres is ready."
