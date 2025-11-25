#!/bin/bash
# ===============================
# User & Role API Test Script (Local)
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

# Generate random test user email and role name
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_USER_EMAIL="testuser_${RANDOM_SUFFIX}@example.com"
TEST_ROLE_NAME="testrole_${RANDOM_SUFFIX}"

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
# CREATE ROLE
# ===============================
echo
echo "=== CREATE ROLE ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/roles/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"$TEST_ROLE_NAME\",
        \"description\": \"Test role created by automated script\"
      }")

# Validate JSON
if ! echo "$CREATE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Create role returned invalid JSON"
  exit 1
fi

echo "$CREATE_RESPONSE" | jq .
NEW_ROLE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')

if [[ -z "$NEW_ROLE_ID" ]]; then
  echo "❌ Failed to extract role ID"
  exit 1
fi

# ===============================
# GET ROLE
# ===============================
echo
echo "=== GET ROLE ==="
GET_RESPONSE=$(curl -s -X GET "$USER_URL/roles/$NEW_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Get role returned invalid JSON"
  exit 1
fi

HTTP_STATUS=$(echo "$GET_RESPONSE" | jq -r '.status_code // empty')
if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ Get role failed, status_code=$HTTP_STATUS"
else
  echo "$GET_RESPONSE" | jq .
fi

# ===============================
# LIST ROLES
# ===============================
echo
echo "=== LIST ROLES ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/roles/" -H "$AUTH_HEADER")
if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "❌ List roles failed, raw response: $LIST_RESPONSE"
fi

HTTP_STATUS=$(echo "$LIST_RESPONSE" | jq -r '.status_code // empty')
if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ List roles failed, status_code=$HTTP_STATUS"
else
  echo "$LIST_RESPONSE" | jq .
fi

# ===============================
# UPDATE ROLE
# ===============================
echo
echo "=== UPDATE ROLE ==="
curl -s -X PUT "$USER_URL/roles/$NEW_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"updated_${TEST_ROLE_NAME}\",
        \"description\": \"Updated role description\"
      }" | jq .

# ===============================
# DELETE ROLE
# ===============================
echo
echo "=== DELETE ROLE ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/roles/$NEW_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$DELETE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Delete role returned invalid JSON"
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
