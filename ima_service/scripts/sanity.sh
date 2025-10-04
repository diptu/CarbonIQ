#!/bin/bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000/api/v1"

# -------------------------
# 1️⃣ Health check
# -------------------------
echo "🔹 Checking Health..."
health_resp=$(curl -s "$BASE_URL/health/" | tr -d '\r')
health_status=$(echo "$health_resp" | jq -r '.details.status // empty')

if [[ "$health_status" == "ok" ]]; then
    echo "✅ Health OK"
else
    echo "❌ Health FAILED"
    echo "Response: $health_resp"
    exit 1
fi

# -------------------------
# 2️⃣ Login
# -------------------------
echo "🔹 Logging in..."
EMAIL="demo@admin.com"
PASSWORD="Hello123"

login_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=$EMAIL&password=$PASSWORD" | tr -d '\r')

HTTP_CODE=$(echo "$login_resp" | tail -n1)
HTTP_BODY=$(echo "$login_resp" | sed '$d')

ACCESS_TOKEN=$(echo "$HTTP_BODY" | jq -r '.details.accessToken // empty')
TENANT_ID=$(echo "$HTTP_BODY" | jq -r '.details.tenantId // empty')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 && -n "$ACCESS_TOKEN" && -n "$TENANT_ID" ]]; then
    echo "✅ Login successful"
    echo "Tenant ID: $TENANT_ID"
else
    echo "❌ Login failed. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 3️⃣ Create User
# -------------------------
echo "🔹 Creating new user..."
NEW_USER_EMAIL="user$(date +%s)@example.com"
NEW_USER_PASSWORD="User123!"

create_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/users/?tenant_id=$TENANT_ID" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
        \"email\": \"$NEW_USER_EMAIL\",
        \"password\": \"$NEW_USER_PASSWORD\",
        \"isActive\": true,
        \"isSuperuser\": false
      }")

HTTP_CODE=$(echo "$create_resp" | tail -n1)
HTTP_BODY=$(echo "$create_resp" | sed '$d')

USER_ID=$(echo "$HTTP_BODY" | jq -r '.details.id // empty')
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 && -n "$USER_ID" ]]; then
    echo "✅ User created: $NEW_USER_EMAIL (ID: $USER_ID)"
else
    echo "❌ Failed to create user. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 3️⃣a Verify initial role is VIEWER
# -------------------------
echo "🔹 Verifying initial role is VIEWER..."
roles_resp=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users/$USER_ID" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$roles_resp" | tail -n1)
HTTP_BODY=$(echo "$roles_resp" | sed '$d')

INITIAL_ROLE=$(echo "$HTTP_BODY" | jq -r '.details.roles[0].name // empty')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 && "$INITIAL_ROLE" == "VIEWER" ]]; then
    echo "✅ Initial role is VIEWER"
else
    echo "❌ Initial role is not VIEWER. Found: $INITIAL_ROLE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 3️⃣b Assign a new MEMBER role (replacing previous)
# -------------------------
echo "🔹 Assigning role: MEMBER..."
assign_resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/users/$USER_ID/roles?role_name=MEMBER&tenant_id=$TENANT_ID" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

HTTP_CODE=$(echo "$assign_resp" | tail -n1)
HTTP_BODY=$(echo "$assign_resp" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    echo "✅ MEMBER role assigned successfully (previous role replaced for this tenant)"
else
    echo "❌ Failed to assign MEMBER role. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 4️⃣ List Users
# -------------------------
echo "🔹 Listing users..."
list_resp=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/users" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$list_resp" | tail -n1)
HTTP_BODY=$(echo "$list_resp" | sed '$d')

echo "$HTTP_BODY" | jq -r '.details.items[] | "\(.id) | \(.email) | Active: \(.isActive) | Roles: \([.roles[].name] | join(","))"'

# -------------------------
# 5️⃣ Deactivate User
# -------------------------
echo "🔹 Deactivating user $USER_ID..."
deactivate_resp=$(curl -s -w "\n%{http_code}" -X POST \
  "$BASE_URL/users/$USER_ID/deactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

HTTP_CODE=$(echo "$deactivate_resp" | tail -n1)
HTTP_BODY=$(echo "$deactivate_resp" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    user_email=$(echo "$HTTP_BODY" | jq -r '.details.email // empty')
    user_roles=$(echo "$HTTP_BODY" | jq -r '.details.roles[].name // empty' | paste -sd "," -)
    echo "✅ User deactivated: $user_email | Roles preserved: $user_roles"
else
    echo "❌ Failed to deactivate user. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 6️⃣ Reactivate User
# -------------------------
echo "🔹 Reactivating user $USER_ID..."
reactivate_resp=$(curl -s -w "\n%{http_code}" -X POST \
  "$BASE_URL/users/$USER_ID/reactivate" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

HTTP_CODE=$(echo "$reactivate_resp" | tail -n1)
HTTP_BODY=$(echo "$reactivate_resp" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    user_email=$(echo "$HTTP_BODY" | jq -r '.details.email // empty')
    user_roles=$(echo "$HTTP_BODY" | jq -r '.details.roles[].name // empty' | paste -sd "," -)
    echo "✅ User reactivated: $user_email | Roles preserved: $user_roles"
else
    echo "❌ Failed to reactivate user. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

# -------------------------
# 7️⃣ Delete User
# -------------------------
echo "🔹 Deleting user $USER_ID..."
delete_resp=$(curl -s -w "\n%{http_code}" -X DELETE \
  "$BASE_URL/users/$USER_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

HTTP_CODE=$(echo "$delete_resp" | tail -n1)
HTTP_BODY=$(echo "$delete_resp" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    echo "✅ User deleted successfully: $USER_ID"
else
    echo "❌ Failed to delete user. HTTP code: $HTTP_CODE"
    echo "Response: $HTTP_BODY"
    exit 1
fi

echo "🎉 All sanity checks passed!"
