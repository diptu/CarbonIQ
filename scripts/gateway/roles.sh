#!/bin/bash
# ===============================
# Gateway + User Service Role API Test Script
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
# Config - URLs
# ===============================
GATEWAY_AUTH_URL="${GATEWAY_AUTH_URL:-http://localhost:9003}"  # gateway auth URL
USER_SERVICE_URL="${USER_SERVICE_URL:-http://localhost:9003}"  # user service URL (roles endpoint)

EMAIL="admin@apple.com"
PASSWORD="Hello123"

# Generate random test role name
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_ROLE_NAME="test_role_${RANDOM_SUFFIX}"

# ===============================
# LOGIN via gateway
# ===============================
echo "=== LOGIN ==="
LOGIN_RESPONSE=$(curl -s -X POST "$GATEWAY_AUTH_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "Raw login response:"
echo "$LOGIN_RESPONSE" | jq .

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" || -z "$REFRESH_TOKEN" ]]; then
  echo "❌ Login failed, aborting further steps."
  exit 1
fi

echo "✅ Login successful. User ID: $(echo "$LOGIN_RESPONSE" | jq -r '.user_id')"
AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

# ===============================
# LIST ROLES (user service)
# ===============================
echo
echo "=== LIST ROLES ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_SERVICE_URL/roles?skip=0&limit=5" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
  ROLE_ID=$(echo "$LIST_RESPONSE" | jq -r '.result.roles[0].id // empty')
else
  echo "⚠️ /roles endpoint not found or returned invalid JSON."
  echo "$LIST_RESPONSE"
  exit 1
fi

# ===============================
# GET SINGLE ROLE
# ===============================
if [[ -n "$ROLE_ID" ]]; then
  echo
  echo "=== GET SINGLE ROLE ==="
  curl -s -X GET "$USER_SERVICE_URL/roles/$ROLE_ID" \
    -H "$AUTH_HEADER" \
    -H "accept: application/json" | jq .
else
  echo "⚠️ No roles found to test GET role endpoint."
fi

# ===============================
# CREATE ROLE
# ===============================
echo
echo "=== CREATE ROLE ==="
CREATE_RESPONSE_RAW=$(curl -s -X POST "$USER_SERVICE_URL/roles" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"$TEST_ROLE_NAME\",
        \"description\": \"Test role created by automated script\"
      }")

echo "Raw response from create:"
echo "$CREATE_RESPONSE_RAW"

if echo "$CREATE_RESPONSE_RAW" | jq empty 2>/dev/null; then
  echo "$CREATE_RESPONSE_RAW" | jq .
  NEW_ROLE_ID=$(echo "$CREATE_RESPONSE_RAW" | jq -r '.result.id // empty')
else
  echo "❌ Failed to create new role. Endpoint missing or returned invalid JSON."
  exit 1
fi

# ===============================
# UPDATE ROLE
# ===============================
echo
echo "=== UPDATE ROLE ==="
curl -s -X PUT "$USER_SERVICE_URL/roles/$NEW_ROLE_ID" \
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
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_SERVICE_URL/roles/$NEW_ROLE_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")
echo "$DELETE_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $DELETE_RESPONSE"

# ===============================
# ✅ FINAL EXECUTION TIME
# ===============================
END_TIME=$(timestamp_ms)
TOTAL_MS=$((END_TIME - START_TIME))
SECONDS=$(echo "scale=2; $TOTAL_MS / 1000" | bc)
MINUTES=$(echo "scale=2; $SECONDS / 60" | bc)

echo ""
echo "✅ Finished!"
echo "⏱️ Total execution time: ${SECONDS}s (${TOTAL_MS}ms) (~${MINUTES} min)"
