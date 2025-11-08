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
EMAIL="admin@apple.com"
PASSWORD="Hello123"

# Test Role & Permission IDs (replace with valid ones in your DB)
TEST_ROLE_ID="ab5b8c8d-483f-4424-8853-4e01d11cbc9b"
TEST_PERMISSION_ID="ab0426e2-f847-4bfa-96d5-cd0aa88f20f2"

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
echo "=== LIST ROLE-PERMISSIONS ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/role-permissions/?skip=0&limit=10" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "🚨 Non-JSON LIST response:"
  echo "$LIST_RESPONSE"
fi

EXISTING_RP_ID=$(echo "$LIST_RESPONSE" 2>/dev/null | jq -r '.result.role_permissions[0].id // empty')

if [[ -n "$EXISTING_RP_ID" ]]; then
  echo
  echo "=== GET SINGLE ROLE-PERMISSION ==="
  GET_RESPONSE=$(curl -s -X GET "$USER_URL/role-permissions/$EXISTING_RP_ID" \
    -H "$AUTH_HEADER" \
    -H "accept: application/json")

  if echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
    echo "$GET_RESPONSE" | jq .
  else
    echo "🚨 Non-JSON GET response:"
    echo "$GET_RESPONSE"
  fi
else
  echo "⚠️ No existing role-permissions found — continuing"
fi

echo
echo "=== CREATE ROLE-PERMISSION ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/role-permissions/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"role_id\": \"$TEST_ROLE_ID\",
        \"permission_id\": \"$TEST_PERMISSION_ID\"
      }")

if echo "$CREATE_RESPONSE" | jq empty 2>/dev/null; then
  echo "$CREATE_RESPONSE" | jq .
  NEW_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')
else
  echo "🚨 Non-JSON CREATE response:"
  echo "$CREATE_RESPONSE"
  exit 1
fi

echo
echo "=== VERIFY CREATION ==="
GET_NEW=$(curl -s -X GET "$USER_URL/role-permissions/$NEW_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$GET_NEW" | jq empty 2>/dev/null; then
  echo "$GET_NEW" | jq .
else
  echo "🚨 Non-JSON GET response:"
  echo "$GET_NEW"
fi

echo
echo "=== DELETE ROLE-PERMISSION ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/role-permissions/$NEW_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$DELETE_RESPONSE" | jq empty 2>/dev/null; then
  echo "$DELETE_RESPONSE" | jq .
else
  echo "🚨 Non-JSON DELETE response:"
  echo "$DELETE_RESPONSE"
fi

END_TIME=$(timestamp_ms)
TOTAL_MS=$((END_TIME - START_TIME))
SECONDS=$(echo "scale=2; $TOTAL_MS / 1000" | bc)

echo ""
echo "✅ Finished!"
echo "⏱️ ${SECONDS}s (${TOTAL_MS}ms)"
