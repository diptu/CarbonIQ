#!/bin/bash
export PYTHONPATH=$(pwd)
set -euo pipefail

# -------------------------
# Colors
# -------------------------
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
RESET="\033[0m"

CHECK="${GREEN}✅${RESET}"
CROSS="${RED}❌${RESET}"
WARN="${YELLOW}⚠️${RESET}"

BASE_URL="http://127.0.0.1:8000/api/v1"

# -------------------------
# Random test user
# -------------------------
RAND_UID=$(uuidgen | cut -c1-8)
TEST_USER_EMAIL="sanity_${RAND_UID}@example.com"
TEST_USER_PASSWORD="password123"

# -------------------------
# Counters
# -------------------------
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

log_pass() { echo " $CHECK $1"; PASS_COUNT=$((PASS_COUNT+1)); }
log_fail() { echo " $CROSS $1"; FAIL_COUNT=$((FAIL_COUNT+1)); }
log_warn() { echo " $WARN $1"; WARN_COUNT=$((WARN_COUNT+1)); }

echo "[sanity] Base URL: $BASE_URL"

# -------------------------
# 1️⃣ Health check
# -------------------------
# -------------------------
# 1️⃣ Health check
# -------------------------
health_resp=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/")
http_code=$(echo "$health_resp" | tail -n1)
health_body=$(echo "$health_resp" | sed '$d')  # remove last line (http_code)

# Try to parse JSON safely
health_status=$(echo "$health_body" | jq -r '.details.status // empty' 2>/dev/null) || {
    echo " $CROSS Failed to parse JSON from health endpoint"
    echo "      Raw response: $health_body"
    exit 1
}

if [[ "$http_code" != "200" ]]; then
    log_fail "Health check returned HTTP $http_code"
    echo "      Response: $health_body"
    exit 1
fi

if [[ "$health_status" == "ok" ]]; then
    log_pass "Health OK"
else
    log_fail "Health FAILED"
    echo "      Response: $health_body"
    exit 1
fi

# -------------------------
# 2️⃣ Login as admin
# -------------------------
ADMIN_EMAIL="admin@caroniq.com"
ADMIN_PASSWORD="Hello123"

login_resp=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
}")

ACCESS_TOKEN=$(echo "$login_resp" | jq -r '.details.access_token // empty')
REFRESH_TOKEN=$(echo "$login_resp" | jq -r '.details.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" ]]; then
    log_fail "Login failed"
    echo "$login_resp"
    exit 1
else
    log_pass "Login successful"
fi

# -------------------------
# 3️⃣ Create test user
# -------------------------
create_resp=$(curl -s -X POST "$BASE_URL/users/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\"
}")

USER_ID=$(echo "$create_resp" | jq -r '.details.id // empty')
if [[ -z "$USER_ID" ]]; then
    log_fail "User creation FAILED"
    echo "$create_resp"
    exit 1
else
    log_pass "User created ($TEST_USER_EMAIL)"
fi

# -------------------------
# 4️⃣ List users
# -------------------------
users_resp=$(curl -s -X GET "$BASE_URL/users/?skip=0&limit=100" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
if [[ "$users_resp" == *"$TEST_USER_EMAIL"* ]]; then
    log_pass "Users list contains test user"
else
    log_fail "Users list FAILED"
fi

# -------------------------
# 5️⃣ Get user by ID
# -------------------------
user_by_id_resp=$(curl -s -X GET "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
if [[ "$user_by_id_resp" == *"$TEST_USER_EMAIL"* ]]; then
    log_pass "Fetched user by ID"
else
    log_fail "Get user by ID FAILED"
fi

# -------------------------
# 6️⃣ Update user email
# -------------------------
UPDATED_EMAIL="updated_${RAND_UID}@example.com"
update_resp=$(curl -s -X PUT "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$UPDATED_EMAIL\",
    \"isActive\": true,
    \"isSuperuser\": false,
    \"password\": \"$TEST_USER_PASSWORD\"
}")
if [[ "$update_resp" == *"$UPDATED_EMAIL"* ]]; then
    log_pass "User updated successfully"
else
    log_fail "Update user FAILED"
    echo "$update_resp"
fi

# -------------------------
# 7️⃣ Assign role (update role)
# -------------------------
assign_resp=$(curl -s -X POST "$BASE_URL/users/${USER_ID}/roles" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --get --data-urlencode "role_name=MEMBER")
if [[ "$assign_resp" == *"MEMBER"* ]]; then
    log_pass "Role assigned/updated"
else
    log_fail "Role assignment FAILED"
    echo "$assign_resp"
fi

# -------------------------
# 8️⃣ Deactivate user
# -------------------------
deact_resp=$(curl -s -X POST "$BASE_URL/users/${USER_ID}/deactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
is_active=$(echo "$deact_resp" | jq -r '.details.isActive // empty')
if [[ "$is_active" == "false" ]]; then
    log_pass "User deactivated"
else
    log_fail "Deactivate FAILED"
    echo "$deact_resp"
fi

# -------------------------
# 9️⃣ Reactivate user
# -------------------------
react_resp=$(curl -s -X POST "$BASE_URL/users/${USER_ID}/reactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
is_active=$(echo "$react_resp" | jq -r '.details.isActive // empty')
if [[ "$is_active" == "true" ]]; then
    log_pass "User reactivated"
else
    log_fail "Reactivate FAILED"
    echo "$react_resp"
fi

# -------------------------
# 🔟 Delete test user
# -------------------------
del_resp=$(curl -s -X DELETE "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
if [[ -z "$del_resp" || "$del_resp" == "{}" ]]; then
    log_pass "User deleted (cleanup)"
else
    log_warn "Cleanup may have failed"
    echo "$del_resp"
fi

# -------------------------
# 📊 Summary
# -------------------------
echo
echo "========== Sanity Summary =========="
echo "  Passed   : $PASS_COUNT"
echo "  Failed   : $FAIL_COUNT"
echo "  Warnings : $WARN_COUNT"
echo "===================================="

if [[ $FAIL_COUNT -gt 0 ]]; then
    exit 1
fi
