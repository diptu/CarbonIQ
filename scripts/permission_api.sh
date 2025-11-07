#!/bin/bash
# ===== Cross-platform millisecond timestamp =====
timestamp_ms() {
  python3 - << 'EOF'
import time
print(int(time.time() * 1000))
EOF
}

START_TIME=$(timestamp_ms)

USER_URL="http://localhost:8000"
AUTH_URL="http://localhost:8001"
EMAIL="admin@carboniq.com"
PASSWORD="Hello123"

# Generate random permission name
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_PERMISSION_NAME="test_permission_${RANDOM_SUFFIX}"

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

echo
echo "=== LIST PERMISSIONS ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/permissions/?skip=0&limit=5" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

echo "$LIST_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $LIST_RESPONSE"

# ✅ Extract first permission ID if exists
PERM_ID=$(echo "$LIST_RESPONSE" | jq -r '.result.permissions[0].id // empty')

if [[ -z "$PERM_ID" ]]; then
  echo "⚠️ No permissions available to test GET/UPDATE. Proceeding to CREATE only."
else
  echo
  echo "=== GET SINGLE PERMISSION ==="
  curl -s -X GET "$USER_URL/permissions/$PERM_ID" \
    -H "$AUTH_HEADER" \
    -H "accept: application/json" | jq .
fi

echo
echo "=== CREATE PERMISSION ==="
CREATE_RESPONSE_RAW=$(curl -s -X POST "$USER_URL/permissions/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"$TEST_PERMISSION_NAME\",
        \"description\": \"Created by automated permission test script\"
      }")

echo "RAW Response:"
echo "$CREATE_RESPONSE_RAW"

# Validate JSON
if echo "$CREATE_RESPONSE_RAW" | jq empty 2>/dev/null; then
  echo "$CREATE_RESPONSE_RAW" | jq .
  NEW_PERM_ID=$(echo "$CREATE_RESPONSE_RAW" | jq -r '.result.id // empty')
else
  echo "❌ Server did not return JSON. Aborting."
  exit 1
fi


echo
echo "=== UPDATE PERMISSION ==="
curl -s -X PUT "$USER_URL/permissions/$NEW_PERM_ID" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"name\": \"updated_${TEST_PERMISSION_NAME}\",
        \"description\": \"Updated permission description\"
      }" | jq .


echo
echo "=== DELETE PERMISSION ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/permissions/$NEW_PERM_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

echo "$DELETE_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $DELETE_RESPONSE"


# ======== Execution Time ==========
END_TIME=$(timestamp_ms)

TOTAL_MS=$((END_TIME - START_TIME))
SECONDS=$(echo "scale=2; $TOTAL_MS / 1000" | bc)
MINUTES=$(echo "scale=2; $SECONDS / 60" | bc)

echo ""
echo "✅ Permission API test complete!"
echo "⏱️ Total execution time: ${SECONDS}s (${TOTAL_MS}ms) (~${MINUTES} min)"
