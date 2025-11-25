#!/bin/bash
# ===============================
# UserRole API Test Script (Local)
# ===============================

# ===== Cross-platform millisecond timestamp =====
timestamp_ms() {
  python3 - << 'EOF'
import time
print(int(time.time() * 1000))
EOF
}

START_TIME=$(timestamp_ms)

# ===============================
# Config - Detect localhost URLs
# ===============================
USER_URL="${USER_URL:-http://localhost:8000}"
AUTH_URL="${AUTH_URL:-http://localhost:8001}"

EMAIL="admin@apple.com"
PASSWORD="Hello123"

# Generate random test user_id and role_id for assignment
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_USER_ID="ffcda680-8316-4a2c-a62b-f35c8a7e3c39" # make sure this exist in DB
TEST_ROLE_ID="2e69a301-4c6b-408a-8654-fb4f3d8ada6f" # make sure this exist in DB

# ===============================
# LOGIN
# ===============================
echo "=== LOGIN ==="
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token // empty')

if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "❌ Login failed, aborting tests."
  exit 1
fi

AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

# ===============================
# CREATE USER_ROLE
# ===============================
echo
echo "=== CREATE USER_ROLE ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/user-roles/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"user_id\": \"$TEST_USER_ID\",
        \"role_id\": \"$TEST_ROLE_ID\"
      }")

# Validate JSON
if ! echo "$CREATE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Create user_role returned invalid JSON"
  exit 1
fi

echo "$CREATE_RESPONSE" | jq .
NEW_USER_ROLE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')

if [[ -z "$NEW_USER_ROLE_ID" ]]; then
  echo "❌ Failed to extract user_role ID"
  exit 1
fi

# ===============================
# GET USER_ROLE
# ===============================
echo
echo "=== GET USER_ROLE ==="
GET_RESPONSE=$(curl -s -X GET "$USER_URL/user-roles/$NEW_USER_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Get user_role returned invalid JSON"
  exit 1
fi

echo "$GET_RESPONSE" | jq .

# ===============================
# LIST USER_ROLES
# ===============================
echo
echo "=== LIST USER_ROLES ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/user-roles/" -H "$AUTH_HEADER")
if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "❌ List user_roles failed, raw response: $LIST_RESPONSE"
fi

# ===============================
# DELETE USER_ROLE
# ===============================
echo
echo "=== DELETE USER_ROLE ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/user-roles/$NEW_USER_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$DELETE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Delete user_role returned invalid JSON"
else
  echo "$DELETE_RESPONSE" | jq .
fi

# ======== Execution Time ==========
END_TIME=$(timestamp_ms)
TOTAL_MS=$((END_TIME - START_TIME))
SECONDS=$(echo "scale=2; $TOTAL_MS / 1000" | bc)
MINUTES=$(echo "scale=2; $SECONDS / 60" | bc)

echo ""
echo "✅ Finished!"
echo "⏱️ Total execution time: ${SECONDS}s (~${MINUTES} min)"
