#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# 🌐 API Configuration
# -----------------------------
API_URL="http://127.0.0.1:8000/api/v1"
PASSWORD="Hello123"

# -----------------------------
# 📊 Global Counters & Storage
# -----------------------------
PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()
