#!/bin/bash
# ===============================
# Permission API Test Script (Local)
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

# Generate random test permission name
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_PERMISSION_NAME="testperm_${RANDOM_SUFFIX}"

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
# CREATE PERMISSION
# ===============================
echo
echo "=== CREATE PERMISSION ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/permissions/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"$TEST_PERMISSION_NAME\",
        \"description\": \"Test permission created by automated script\"
      }")

# Validate JSON
if ! echo "$CREATE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Create permission returned invalid JSON"
  exit 1
fi

echo "$CREATE_RESPONSE" | jq .
NEW_PERMISSION_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')

if [[ -z "$NEW_PERMISSION_ID" ]]; then
  echo "❌ Failed to extract permission ID"
  exit 1
fi

# ===============================
# GET PERMISSION
# ===============================
echo
echo "=== GET PERMISSION ==="
GET_RESPONSE=$(curl -s -X GET "$USER_URL/permissions/$NEW_PERMISSION_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Get permission returned invalid JSON"
  exit 1
fi

HTTP_STATUS=$(echo "$GET_RESPONSE" | jq -r '.status_code // empty')
if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ Get permission failed, status_code=$HTTP_STATUS"
else
  echo "$GET_RESPONSE" | jq .
fi

# ===============================
# LIST PERMISSIONS
# ===============================
echo
echo "=== LIST PERMISSIONS ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/permissions/" -H "$AUTH_HEADER")
if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "❌ List permissions failed, raw response: $LIST_RESPONSE"
fi

HTTP_STATUS=$(echo "$LIST_RESPONSE" | jq -r '.status_code // empty')
if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ List permissions failed, status_code=$HTTP_STATUS"
else
  echo "$LIST_RESPONSE" | jq .
fi

# ===============================
# UPDATE PERMISSION
# ===============================
echo
echo "=== UPDATE PERMISSION ==="
curl -s -X PUT "$USER_URL/permissions/$NEW_PERMISSION_ID" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"updated_${TEST_PERMISSION_NAME}\",
        \"description\": \"Updated permission description\"
      }" | jq .

# ===============================
# DELETE PERMISSION
# ===============================
echo
echo "=== DELETE PERMISSION ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/permissions/$NEW_PERMISSION_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$DELETE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Delete permission returned invalid JSON"
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
