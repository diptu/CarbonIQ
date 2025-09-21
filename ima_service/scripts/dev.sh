#!/usr/bin/env bash
# Start dev server (reload). Usage: PORT=8000 ./dev.sh
set -Eeuo pipefail

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

# go to service root
cd "$(dirname "$0")/.."

uv run uvicorn main:app --reload --host "$HOST" --port "$PORT"
