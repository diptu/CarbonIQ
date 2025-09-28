#!/bin/bash
export PYTHONPATH=$(pwd)
# Alembic helpers:
# ./migrate.sh up | down [-1] | rev "msg" | current
set -Eeuo pipefail

cd "$(dirname "$0")/.."

cmd="${1:-up}"; shift || true
case "$cmd" in
  up)       uv run alembic -c alembic.ini upgrade head ;;
  down)     uv run alembic -c alembic.ini downgrade "${1:--1}" ;;
  rev)
    uv run alembic -c alembic.ini upgrade head
    uv run alembic -c alembic.ini revision --autogenerate -m "${1:-auto}"
    ;;
  current)  uv run alembic -c alembic.ini current ;;
  *) echo "unknown cmd: $cmd"; exit 2 ;;
esac
