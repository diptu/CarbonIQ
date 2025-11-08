#!/bin/bash

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

TEST_USER_ID="5867920e-166a-402f-aef7-9cc2e7f5a6e2"
TEST_ROLE_ID="ab5b8c8d-483f-4424-8853-4e01d11cbc9b"

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
echo "=== LIST USER ROLES ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/user-roles/?skip=0&limit=10" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "🚨 Non-JSON LIST response:"
  echo "$LIST_RESPONSE"
fi

EXISTING_UR_ID=$(echo "$LIST_RESPONSE" 2>/dev/null | jq -r '.result.user_roles[0].id // empty')

if [[ -n "$EXISTING_UR_ID" ]]; then
  echo
  echo "=== GET SINGLE USER-ROLE ==="
  GET_RESPONSE=$(curl -s -X GET "$USER_URL/user-roles/$EXISTING_UR_ID" \
    -H "$AUTH_HEADER" \
    -H "accept: application/json")

  if echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
    echo "$GET_RESPONSE" | jq .
  else
    echo "🚨 Non-JSON GET response:"
    echo "$GET_RESPONSE"
  fi
else
  echo "⚠️ No existing user-roles found — continuing"
fi


echo
echo "=== CREATE USER ROLE ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/user-roles/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"user_id\": \"$TEST_USER_ID\",
        \"role_id\": \"$TEST_ROLE_ID\"
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
GET_NEW=$(curl -s -X GET "$USER_URL/user-roles/$NEW_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if echo "$GET_NEW" | jq empty 2>/dev/null; then
  echo "$GET_NEW" | jq .
else
  echo "🚨 Non-JSON GET response:"
  echo "$GET_NEW"
fi


echo
echo "=== DELETE USER ROLE ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/user-roles/$NEW_ID" \
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
