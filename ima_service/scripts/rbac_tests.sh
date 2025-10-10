#!/usr/bin/env bash
set -uo pipefail

API_URL="http://127.0.0.1:8000/api/v1"
PASSWORD="Hello123"

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

# -----------------------------
# Tenant mapping
# -----------------------------
TENANT_IDS=(
    "Apple Inc.=77ed9f5e-12e9-430d-bada-fa6efa24e68d"
    "Orchard Apple=1ab72589-b940-4dc7-9f6f-4d1cb9d804dc"
    "Grove Orange=d18014c1-cc70-422e-965c-a377f02b4d55"
    "Peanut Corp.=0270a955-3389-4989-9bd1-5c3acf2f795a"
)

get_tenant_id() {
    local TARGET="$1"
    for item in "${TENANT_IDS[@]}"; do
        IFS="=" read -r NAME ID <<< "$item"
        if [[ "$NAME" == "$TARGET" ]]; then
            echo "$ID"
            return
        fi
    done
    echo ""
}

# -----------------------------
# Login function
# -----------------------------
login() {
    local EMAIL="$1"
    local PASS="$2"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/login" \
        -H "accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$EMAIL\", \"password\": \"$PASS\"}")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
        ACCESS_TOKEN=$(echo "$BODY" | jq -r '.access_token // empty')
        TENANT_ID=$(echo "$BODY" | jq -r '.tenant_id // empty')
        echo -e "${GREEN}✅ Logged in: $EMAIL | Tenant ID: $TENANT_ID${RESET}"
        return 0
    else
        echo -e "${RED}❌ Login failed for $EMAIL | HTTP Code: $HTTP_CODE${RESET}"
        echo "$BODY"
        return 1
    fi
}

# -----------------------------
# Fetch users
# -----------------------------
fetch_users() {
    local TOKEN="$1"
    local TENANT="$2"
    curl -s -w "\n%{http_code}" -X GET "$API_URL/users/?skip=0&limit=10&tenant_id=$TENANT" \
        -H "Authorization: Bearer $TOKEN" \
        -H "accept: application/json"
}

# -----------------------------
# Create user
# -----------------------------
create_user() {
    local TOKEN="$1"
    local TENANT="$2"
    local EMAIL="$3"
    local PASS="$4"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/?tenant_id=$TENANT" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\",\"full_name\":\"Test User\",\"is_active\":true}")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    echo "$HTTP_CODE|$BODY"
}

# -----------------------------
# Test cases
# -----------------------------

# Login tests (#1-7)
LOGIN_TESTS=(
"admin@apple.com|Apple Inc.|Success"
"billing@orchard.apple.com|Orchard Apple|Success"
"admin@orange.com|Grove Orange|Success"
"admin@peanut.com|Peanut Corp.|Success"
"admin@banana.com|Non-existent|Fail"
"admin@apple.com|Apple Inc.|FailPassword"
"inactive@apple.com|Apple Inc.|FailInactive"
)

# User listing / read tests (#8-12)
LIST_USERS_TESTS=(
"billing@orchard.apple.com|Orchard Apple|OwnTenant|Success"
"billing@orchard.apple.com|Apple Inc.|ParentTenant|Fail"
"billing@orchard.apple.com|Orange Ltd.|Unrelated|Fail"
"admin@apple.com|Apple Inc.|AdminOwnAndChild|Success"
"superadmin@carboniq.com|All|SuperAdmin|Success"
)

# User creation tests (#13-19)
CREATE_USER_TESTS=(
"admin@apple.com|Apple Inc.|MEMBER|Success"
"admin@apple.com|Orchard Apple|MEMBER|Success"
"admin@apple.com|Orange Ltd.|MEMBER|Fail"
"admin@apple.com|Apple Inc.|MEMBER|Duplicate"
"admin@peanut.com|Peanut Corp.|MEMBER|Success"
"admin@peanut.com|Non-existent|MEMBER|Fail"
"billing@orchard.apple.com|Orchard Apple|ADMIN|Fail"
)

# -----------------------------
# Counters
# -----------------------------
PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()
SERIAL=1

echo "============================================"
echo "🌟 RBAC API Test Start"
echo "============================================"

# -----------------------------
# Run Login Tests
# -----------------------------
echo "🔹 Running Login Tests"
for CASE in "${LOGIN_TESTS[@]}"; do
    IFS='|' read -r USER TENANT EXPECT <<< "$CASE"

    if [[ "$EXPECT" == "FailPassword" ]]; then
        login "$USER" "WrongPassword"
    else
        login "$USER" "$PASSWORD"
    fi

    RET=$?

    if [[ $RET -eq 0 && "$EXPECT" == "Success" ]]; then
        STATUS="${GREEN}✅${RESET}"
        ACTUAL="Login successful"
        ((PASS_COUNT++))
    elif [[ $RET -ne 0 && "$EXPECT" != "Success" ]]; then
        STATUS="${GREEN}✅${RESET}"
        ACTUAL="Expected failure"
        ((PASS_COUNT++))
    else
        STATUS="${RED}❌${RESET}"
        ACTUAL="Unexpected result"
        ((FAIL_COUNT++))
    fi

    RESULTS+=("| $SERIAL | LOGIN | $USER | $TENANT | $EXPECT | $ACTUAL | $STATUS |")
    ((SERIAL++))
done

# -----------------------------
# Run User Listing Tests
# -----------------------------
echo "🔹 Running User Listing Tests"
for CASE in "${LIST_USERS_TESTS[@]}"; do
    IFS='|' read -r USER TENANT TYPE EXPECT <<< "$CASE"

    login "$USER" "$PASSWORD"
    RET=$?
    if [[ $RET -ne 0 ]]; then
        STATUS="${RED}❌${RESET}"
        ACTUAL="Login failed"
        ((FAIL_COUNT++))
    else
        TENANT_ID=$(get_tenant_id "$TENANT")
        RESP=$(fetch_users "$ACCESS_TOKEN" "$TENANT_ID")
        HTTP_CODE=$(echo "$RESP" | tail -n1)
        BODY=$(echo "$RESP" | sed '$d')

        if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 && "$EXPECT" == "Success" ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="Fetched users successfully"
            ((PASS_COUNT++))
        elif [[ "$HTTP_CODE" -ge 400 && "$EXPECT" != "Success" ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="Expected failure"
            ((PASS_COUNT++))
        else
            STATUS="${RED}❌${RESET}"
            ACTUAL="Unexpected result (HTTP $HTTP_CODE)"
            ((FAIL_COUNT++))
        fi
    fi
    RESULTS+=("| $SERIAL | LIST_USERS | $USER | $TENANT | $EXPECT | $ACTUAL | $STATUS |")
    ((SERIAL++))
done

# # -----------------------------
# # Run User Creation Tests
# # -----------------------------
# echo "🔹 Running User Creation Tests"
# for CASE in "${CREATE_USER_TESTS[@]}"; do
#     IFS='|' read -r USER TENANT ROLE EXPECT <<< "$CASE"

#     login "$USER" "$PASSWORD"
#     RET=$?
#     if [[ $RET -ne 0 ]]; then
#         STATUS="${RED}❌${RESET}"
#         ACTUAL="Login failed"
#         ((FAIL_COUNT++))
#     else
#         TENANT_ID=$(get_tenant_id "$TENANT")
#         RANDOM_UID=$(uuidgen)
#         NEW_USER_EMAIL="test_${RANDOM_UID}@example.com"
#         RESULT=$(create_user "$ACCESS_TOKEN" "$TENANT_ID" "$NEW_USER_EMAIL" "$PASSWORD")
#         HTTP_CODE=$(echo "$RESULT" | cut -d'|' -f1)

#         if [[ "$EXPECT" == "Success" && "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
#             STATUS="${GREEN}✅${RESET}"
#             ACTUAL="User created"
#             ((PASS_COUNT++))
#         elif [[ "$EXPECT" == "Fail" && "$HTTP_CODE" -ge 400 ]]; then
#             STATUS="${GREEN}✅${RESET}"
#             ACTUAL="Expected failure"
#             ((PASS_COUNT++))
#         elif [[ "$EXPECT" == "Duplicate" && "$HTTP_CODE" -eq 400 ]]; then
#             STATUS="${GREEN}✅${RESET}"
#             ACTUAL="Duplicate handled"
#             ((PASS_COUNT++))
#         else
#             STATUS="${RED}❌${RESET}"
#             ACTUAL="Unexpected result (HTTP $HTTP_CODE)"
#             ((FAIL_COUNT++))
#         fi
#     fi
#     RESULTS+=("| $SERIAL | CREATE_USER | $USER | $TENANT | $EXPECT | $ACTUAL | $STATUS |")
#     ((SERIAL++))
# done

# -----------------------------
# Summary
# -----------------------------
echo "============================================"
echo "🌟 RBAC API Test Completed"
echo "✅ Passed: $PASS_COUNT | ❌ Failed: $FAIL_COUNT"
echo "--------------------------------------------"
echo -e "| S.No | Endpoint | User | Tenant | Expected | Actual | Status |"
echo -e "|------|---------|------|--------|---------|--------|--------|"
for LINE in "${RESULTS[@]}"; do
    echo -e "$LINE"
done
echo "============================================"
