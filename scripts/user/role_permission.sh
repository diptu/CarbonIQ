#!/bin/bash
# ============================================
# RolePermission API Test Script (Local)
# ============================================

# ===== Cross-platform millisecond timestamp =====
timestamp_ms() {
  python3 - << 'EOF'
import time
print(int(time.time() * 1000))
EOF
}

START_TIME=$(timestamp_ms)

# ============================================
# Config - Detect localhost URLs
# ============================================
USER_URL="${USER_URL:-http://localhost:8000}"
AUTH_URL="${AUTH_URL:-http://localhost:8001}"

EMAIL="admin@apple.com"
PASSWORD="Hello123"

# Use valid IDs that exist in DB
TEST_ROLE_ID="2e69a301-4c6b-408a-8654-fb4f3d8ada6f"        # Ensure exists
TEST_PERMISSION_ID="91962990-dc9f-482c-935c-3f6ad5230ab7"  # Ensure exists

# ============================================
# LOGIN
# ============================================
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

# ============================================
# CREATE ROLE_PERMISSION
# ============================================
echo
echo "=== CREATE ROLE_PERMISSION ==="
CREATE_RESPONSE=$(curl -s -X POST "$USER_URL/role-permissions/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"role_id\": \"$TEST_ROLE_ID\",
        \"permission_id\": \"$TEST_PERMISSION_ID\"
      }")

# Validate JSON
if ! echo "$CREATE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Create role_permission returned invalid JSON"
  exit 1
fi

echo "$CREATE_RESPONSE" | jq .

NEW_RP_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id // empty')

if [[ -z "$NEW_RP_ID" ]]; then
  echo "❌ Failed to extract role_permission ID"
  exit 1
fi

# ============================================
# GET ROLE_PERMISSION
# ============================================
echo
echo "=== GET ROLE_PERMISSION ==="
GET_RESPONSE=$(curl -s -X GET "$USER_URL/role-permissions/$NEW_RP_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$GET_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Get role_permission returned invalid JSON"
  exit 1
fi

echo "$GET_RESPONSE" | jq .

# ============================================
# LIST ROLE_PERMISSIONS
# ============================================
echo
echo "=== LIST ROLE_PERMISSIONS ==="
LIST_RESPONSE=$(curl -s -X GET "$USER_URL/role-permissions/" -H "$AUTH_HEADER")

if echo "$LIST_RESPONSE" | jq empty 2>/dev/null; then
  echo "$LIST_RESPONSE" | jq .
else
  echo "❌ List role_permissions failed, raw response:"
  echo "$LIST_RESPONSE"
fi

# ============================================
# DELETE ROLE_PERMISSION
# ============================================
echo
echo "=== DELETE ROLE_PERMISSION ==="
DELETE_RESPONSE=$(curl -s -X DELETE "$USER_URL/role-permissions/$NEW_RP_ID" \
  -H "$AUTH_HEADER" \
  -H "accept: application/json")

if ! echo "$DELETE_RESPONSE" | jq empty 2>/dev/null; then
  echo "❌ Delete role_permission returned invalid JSON"
else
  echo "$DELETE_RESPONSE" | jq .
fi

# ===== Execution Time =====
END_TIME=$(timestamp_ms)
TOTAL_MS=$((END_TIME - START_TIME))
SECONDS=$(echo "scale=2; $TOTAL_MS / 1000" | bc)
MINUTES=$(echo "scale=2; $SECONDS / 60" | bc)

echo ""
echo "✅ Finished!"
echo "⏱️ Total execution time: ${SECONDS}s (~${MINUTES} min)"
