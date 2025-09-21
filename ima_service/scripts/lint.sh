#!/usr/bin/env bash
# Lint & typecheck. Usage: ./lint.sh
set -Eeuo pipefail

cd "$(dirname "$0")/.."

uv run ruff check app
uv run pylint app || true
uv run mypy app
