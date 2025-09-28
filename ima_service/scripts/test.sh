#!/bin/bash
export PYTHONPATH=$(pwd)
# Test runner. Set COVERAGE=1 for coverage. Args passed to pytest.
set -Eeuo pipefail

cd "$(dirname "$0")/.."

if [[ "${COVERAGE:-0}" == "1" ]]; then
  uv run pytest --cov=app --cov-report=term-missing "$@"
else
  uv run pytest -q "$@"
fi
