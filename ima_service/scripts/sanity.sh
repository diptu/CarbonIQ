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
health_resp=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/")
http_code=$(echo "$health_resp" | tail -n1)
health_body=$(echo "$health_resp" | sed '$d')

health_status=$(echo "$health_body" | jq -r '.details.status // empty' 2>/dev/null) || {
    log_fail "Failed to parse JSON from health endpoint"
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
ADMIN_EMAIL="demo@admin.com"
ADMIN_PASSWORD="Hello123"

login_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
}")

http_code=$(echo "$login_resp" | tail -n1)
login_body=$(echo "$login_resp" | sed '$d')

ACCESS_TOKEN=$(echo "$login_body" | jq -r '.details.accessToken // empty' 2>/dev/null) || {
    log_fail "Failed to parse JSON from login endpoint (access token)"
    echo "      Raw response: $login_body"
    exit 1
}

REFRESH_TOKEN=$(echo "$login_body" | jq -r '.details.refreshToken // empty' 2>/dev/null) || {
    log_fail "Failed to parse JSON from login endpoint (refresh token)"
    echo "      Raw response: $login_body"
    exit 1
}

if [[ "$http_code" != "200" || -z "$ACCESS_TOKEN" ]]; then
    log_fail "Login failed (HTTP $http_code)"
    echo "      Response: $login_body"
    exit 1
else
    log_pass "Login successful"
fi

# -------------------------
# 3️⃣ Token refresh
# -------------------------
refresh_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/refresh" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"refreshToken\": \"$REFRESH_TOKEN\"
}")

http_code=$(echo "$refresh_resp" | tail -n1)
refresh_body=$(echo "$refresh_resp" | sed '$d')
NEW_ACCESS_TOKEN=$(echo "$refresh_body" | jq -r '.accessToken // empty' 2>/dev/null)

if [[ "$http_code" != "200" || -z "$NEW_ACCESS_TOKEN" ]]; then
    log_fail "Token refresh failed (HTTP $http_code)"
    echo "      Response: $refresh_body"
else
    log_pass "Token refresh successful"
    ACCESS_TOKEN="$NEW_ACCESS_TOKEN"
fi

# -------------------------
# 4️⃣ Create test user
# -------------------------
create_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/users/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\",
    \"isActive\": true,
    \"isSuperuser\": false
}")

http_code=$(echo "$create_resp" | tail -n1)
create_body=$(echo "$create_resp" | sed '$d')

USER_ID=$(echo "$create_body" | jq -r '.details.id // empty' 2>/dev/null) || {
    log_fail "Failed to parse JSON from create user endpoint"
    echo "      Raw response: $create_body"
    exit 1
}

if [[ "$http_code" != "201" || -z "$USER_ID" ]]; then
    log_fail "User creation FAILED (HTTP $http_code)"
    echo "      Response: $create_body"
else
    log_pass "User created ($TEST_USER_EMAIL)"
fi

# -------------------------
# 5️⃣ List users
# -------------------------
users_resp=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users/?skip=0&limit=100" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
http_code=$(echo "$users_resp" | tail -n1)
users_body=$(echo "$users_resp" | sed '$d')

if [[ "$http_code" != "200" ]]; then
    log_fail "Users list failed (HTTP $http_code)"
    echo "      Response: $users_body"
elif [[ "$users_body" == *"$TEST_USER_EMAIL"* ]]; then
    log_pass "Users list contains test user"
else
    log_fail "Users list FAILED"
fi

# -------------------------
# 6️⃣ Get user by ID
# -------------------------
user_by_id_resp=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
http_code=$(echo "$user_by_id_resp" | tail -n1)
user_by_id_body=$(echo "$user_by_id_resp" | sed '$d')

if [[ "$http_code" != "200" ]]; then
    log_fail "Get user by ID failed (HTTP $http_code)"
    echo "      Response: $user_by_id_body"
elif [[ "$user_by_id_body" == *"$TEST_USER_EMAIL"* ]]; then
    log_pass "Fetched user by ID"
else
    log_fail "Get user by ID FAILED"
fi

# -------------------------
# 7️⃣ Update user
# -------------------------
update_resp=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"isSuperuser\": true
}")

http_code=$(echo "$update_resp" | tail -n1)
update_body=$(echo "$update_resp" | sed '$d')

if [[ "$http_code" != "200" ]]; then
    log_fail "User update FAILED (HTTP $http_code)"
    echo "      Response: $update_body"
else
    log_pass "User updated successfully"
fi

# -------------------------
# 8️⃣ Deactivate user
# -------------------------
deactivate_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/users/${USER_ID}/deactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
http_code=$(echo "$deactivate_resp" | tail -n1)
if [[ "$http_code" != "200" ]]; then
    log_fail "Deactivate user FAILED"
else
    log_pass "Deactivate user successful"
fi

# -------------------------
# 9️⃣ Reactivate user
# -------------------------
reactivate_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/users/${USER_ID}/reactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
http_code=$(echo "$reactivate_resp" | tail -n1)
if [[ "$http_code" != "200" ]]; then
    log_fail "Reactivate user FAILED"
else
    log_pass "Reactivate user successful"
fi

# -------------------------
# 10️⃣ Roles list
# -------------------------
roles_resp=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/roles/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")
http_code=$(echo "$roles_resp" | tail -n1)
roles_body=$(echo "$roles_resp" | sed '$d')

# check HTTP code
if [[ "$http_code" != "200" ]]; then
    log_fail "Roles list fetch FAILED (HTTP $http_code)"
    echo "      Response: $roles_body"
else
    # optionally check if at least one role exists
    first_role=$(echo "$roles_body" | jq -r '.details[0].name // empty')
    if [[ -n "$first_role" ]]; then
        log_pass "Roles list fetched (found role: $first_role)"
    else
        log_warn "Roles list fetched but empty"
    fi
fi

# -------------------------
# 11️⃣ Logout
# -------------------------
logout_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")
http_code=$(echo "$logout_resp" | tail -n1)
logout_body=$(echo "$logout_resp" | sed '$d')

if [[ "$http_code" != "200" ]]; then
    log_fail "Logout FAILED (HTTP $http_code)"
    echo "      Response: $logout_body"
else
    log_pass "Logout successful"
fi

# -------------------------
# 12️⃣ Delete test user
# -------------------------
delete_resp=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/users/${USER_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
http_code=$(echo "$delete_resp" | tail -n1)
delete_body=$(echo "$delete_resp" | sed '$d')

if [[ "$http_code" != "204" ]]; then
    log_fail "Delete user FAILED (HTTP $http_code)"
    echo "      Response: $delete_body"
else
    log_pass "Delete user successful"
fi


# -------------------------
# Summary
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
