#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

# Check symbols
CHECK="${GREEN}✅${RESET}"
CROSS="${RED}❌${RESET}"

BASE_URL="http://127.0.0.1:8000/api/v1"
TEST_USER_EMAIL="newuser@example.com"
TEST_USER_PASSWORD="password123"
TEST_USER_ROLE="viewer"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="secret"

echo "[sanity] Base URL: $BASE_URL"

# 1️⃣ Health check
echo "[sanity] Trying health endpoint: $BASE_URL/health"
health_resp=$(curl -s "$BASE_URL/health")
if [[ "$health_resp" == *"ok"* ]]; then
    echo " $CHECK Health -> /health"
    echo "      $health_resp"
else
    echo " $CROSS Health -> /health"
    echo "      Response: $health_resp"
    exit 1
fi

# 2️⃣ Login as admin
echo "[sanity] Logging in as $ADMIN_EMAIL"
login_resp=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD")

ACCESS_TOKEN=$(echo "$login_resp" | jq -r '.access_token // empty')
REFRESH_TOKEN=$(echo "$login_resp" | jq -r '.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" ]]; then
    echo " $CROSS Login failed for $ADMIN_EMAIL"
    echo "      Response: $login_resp"
    exit 1
else
    echo " $CHECK Login -> /auth/login"
    echo "      $login_resp"
fi

# 3️⃣ Refresh token
echo "[sanity] Refreshing access token"
refresh_resp=$(curl -s -X POST "$BASE_URL/auth/refresh" \
    -H "Content-Type: application/json" \
    -d "{
        \"body\": {\"refresh_token\": \"$REFRESH_TOKEN\"}
    }")

if [[ "$refresh_resp" == *"access_token"* ]]; then
    echo " $CHECK Refresh -> /auth/refresh"
    echo "      $refresh_resp"
else
    echo " $CROSS Refresh -> /auth/refresh"
    echo "      $refresh_resp"
    exit 1
fi

# 4️⃣ Create test user
echo "[sanity] Creating test user"
create_resp=$(curl -s -X POST "$BASE_URL/users" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"password\": \"$TEST_USER_PASSWORD\",
    \"role\": \"$TEST_USER_ROLE\"
}")

USER_ID=$(echo "$create_resp" | jq -r '.id // empty')

if [[ -z "$USER_ID" ]]; then
    echo " $CROSS Create user -> /users"
    echo "      $create_resp"
    exit 1
else
    echo " $CHECK Create user -> /users"
    echo "      $create_resp"
fi

# 5️⃣ Get users list
echo "[sanity] Fetching users list"
users_resp=$(curl -s -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$users_resp" == *"$TEST_USER_EMAIL"* ]]; then
    echo " $CHECK Get users -> /users"
    echo "      $users_resp"
else
    echo " $CROSS Get users -> /users"
    echo "      $users_resp"
    exit 1
fi

# 6️⃣ Get current user
echo "[sanity] Get current user"
me_resp=$(curl -s -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$me_resp" == *"$ADMIN_EMAIL"* ]]; then
    echo " $CHECK Get current user -> /users/me"
    echo "      $me_resp"
else
    echo " $CROSS Get current user -> /users/me"
    echo "      $me_resp"
    exit 1
fi

# 7️⃣ Secure ping
echo "[sanity] Secure ping"
ping_resp=$(curl -s -X GET "$BASE_URL/secure/ping" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$ping_resp" == *"ok"* ]]; then
    echo " $CHECK Secure ping -> /secure/ping"
    echo "      $ping_resp"
else
    echo " $CROSS Secure ping -> /secure/ping"
    echo "      $ping_resp"
fi

# 8️⃣ Owner-only route
echo "[sanity] Owner-only access"
owner_resp=$(curl -s -X GET "$BASE_URL/secure/owner" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$owner_resp" == *"ok"* ]]; then
    echo " $CHECK Owner-only -> /secure/owner"
    echo "      $owner_resp"
else
    echo " $CROSS Owner-only -> /secure/owner"
    echo "      $owner_resp"
fi

# 9️⃣ Editor-or-owner route
echo "[sanity] Editor-or-owner access"
editor_resp=$(curl -s -X GET "$BASE_URL/secure/editor-or-owner" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$editor_resp" == *"ok"* ]]; then
    echo " $CHECK Editor-or-owner -> /secure/editor-or-owner"
    echo "      $editor_resp"
else
    echo " $CROSS Editor-or-owner -> /secure/editor-or-owner"
    echo "      $editor_resp"
fi

# 🔟 Delete test user
echo "[sanity] Deleting test user"
delete_resp=$(curl -s -X DELETE "$BASE_URL/users/$USER_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ "$delete_resp" == *"{}"* || -z "$delete_resp" ]]; then
    echo " $CHECK Delete user -> /users/$USER_ID"
else
    echo " $CROSS Delete user -> /users/$USER_ID"
    echo "      $delete_resp"
fi

# 1️⃣1️⃣ Logout
echo "[sanity] Logging out"
logout_resp=$(curl -s -X POST "$BASE_URL/auth/logout" \
    -H "Content-Type: application/json" \
    -d "{
        \"body\": {\"refresh_token\": \"$REFRESH_TOKEN\", \"all\": true}
    }")

if [[ "$logout_resp" == *"detail"* ]]; then
    echo " $CHECK Logout -> /auth/logout"
    echo "      $logout_resp"
else
    echo " $CROSS Logout -> /auth/logout"
    echo "      $logout_resp"
fi

echo
echo "Sanity summary: Done ✅"
