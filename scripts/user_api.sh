#!/bin/bash
# ===============================
# User API Test Script (Local)
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
# Avoid using 0.0.0.0 in client requests
USER_URL="${USER_URL:-http://localhost:8000}"
AUTH_URL="${AUTH_URL:-http://localhost:8001}"

EMAIL="admin@apple.com"
PASSWORD="Hello123"

# Generate random test user email
RANDOM_SUFFIX=$(date +%s%N | sha256sum | head -c 6)
TEST_USER_EMAIL="testuser_${RANDOM_SUFFIX}@example.com"

# ===============================
# LOGIN
# ===============================
echo "=== LOGIN ==="
echo "Trying login via $AUTH_URL/auth/login"

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
# LIST USERS
# ===============================
echo
echo "=== LIST USERS ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/users/?skip=0&limit=5" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")
echo "$LIST_RESPONSE" | jq .

USER_ID=$(echo "$LIST_RESPONSE" | jq -r '.result.users[0].id // empty')
if [[ -z "$USER_ID" ]]; then
  echo "⚠️ No users found to test further endpoints."
  exit 1
fi

# ===============================
# GET SINGLE USER
# ===============================
echo
echo "=== GET SINGLE USER ==="
curl -s -X GET "$USER_URL/users/$USER_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json" | jq .

# ===============================
# CREATE USER
# ===============================
echo
echo "=== CREATE USER ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/users/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"email\": \"$TEST_USER_EMAIL\",
        \"password\": \"Test1234\",
        \"is_superuser\": false
      }")
echo "$CREATE_RESPONSE" | jq .

NEW_USER_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')
if [[ -z "$NEW_USER_ID" ]]; then
  echo "❌ Failed to create new user, skipping update/activate/deactivate/delete tests."
  exit 1
fi

# ===============================
# UPDATE USER
# ===============================
echo
echo "=== UPDATE USER ==="
curl -s -X PUT "$USER_URL/users/$NEW_USER_ID" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"email\": \"updated_${TEST_USER_EMAIL}\",
        \"password\": \"Test1234Updated\",
        \"is_superuser\": false
      }" | jq .

# ===============================
# ACTIVATE USER
# ===============================
echo
echo "=== ACTIVATE USER ==="
ACTIVATE_RESPONSE=$(curl -s -X POST "$USER_URL/users/$NEW_USER_ID/activate" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json")
echo "$ACTIVATE_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $ACTIVATE_RESPONSE"

# ===============================
# DEACTIVATE USER
# ===============================
echo
echo "=== DEACTIVATE USER ==="
DEACTIVATE_RESPONSE=$(curl -s -X POST "$USER_URL/users/$NEW_USER_ID/deactivate" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json")
echo "$DEACTIVATE_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $DEACTIVATE_RESPONSE"

# ===============================
# DELETE USER
# ===============================
echo
echo "=== DELETE USER ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/users/$NEW_USER_ID" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json")
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
