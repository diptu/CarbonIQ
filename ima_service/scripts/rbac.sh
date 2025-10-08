#!/usr/bin/env bash
set -euo pipefail

API_URL="http://127.0.0.1:8000/api/v1"
PASSWORD="Hello123"

# -----------------------------
# ✅ Colors
# -----------------------------
GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

# -----------------------------
# ✅ Helper Functions
# -----------------------------
function login() {
    local EMAIL="$1"
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "accept: application/json" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=$EMAIL&password=$PASSWORD")

    if ! echo "$LOGIN_RESPONSE" | jq empty >/dev/null 2>&1; then
        echo -e "${RED}❌ Login response not valid JSON for $EMAIL:${RESET}"
        echo "$LOGIN_RESPONSE"
        return 1
    fi

    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.details.accessToken // empty')
    TENANT_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.details.tenantId // empty')

    if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
        echo -e "${RED}❌ Login failed for $EMAIL${RESET}"
        echo "$LOGIN_RESPONSE"
        return 1
    fi

    echo -e "${GREEN}✅ Logged in: $EMAIL | Tenant ID: $TENANT_ID${RESET}"
    return 0
}

function fetch_users() {
    local TOKEN="$1"
    local TENANT="$2"
    curl -s -X GET "$API_URL/users/?skip=0&limit=10&tenant_id=$TENANT" \
        -H "Authorization: Bearer $TOKEN" \
        -H "accept: application/json"
}

function create_user() {
    local TOKEN="$1"
    local TENANT="$2"
    local EMAIL="$3"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/?tenant_id=$TENANT" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$EMAIL\",
            \"password\": \"$PASSWORD\"
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    echo "$HTTP_CODE|$BODY"
}

# -----------------------------
# 🌱 Test Cases
# -----------------------------
LOGIN_TESTS=(
"admin@apple.com|Apple Inc."
"billing@orchard.apple.com|Orchard Apple"
"admin@orange.com|Grove Orange"
"admin@peanut.com|Peanut Corp."
"admin@peanut.com|NonExistent"
)

FETCH_USERS_TESTS=(
"billing@orchard.apple.com|Orchard Apple|pass"
"billing@orchard.apple.com|Apple Inc.|fail"
)

CREATE_USER_TESTS=(
"admin@apple.com|Apple Inc.|pass"
"admin@apple.com|Orchard Apple|pass"
"admin@apple.com|Orange Ltd.|fail"
"billing@orchard.apple.com|Orchard Apple|integrity"
"admin@orange.com|Grove Orange|pass"
"admin@peanut.com|Peanut Corp.|pass"
"admin@peanut.com|NonExistent|fail"
)

# -----------------------------
# 🔹 Tenant Mapping
# -----------------------------
TENANT_NAMES=("Apple Inc." "Orchard Apple" "Summit Apple" "Harbor Apple" "Orange Ltd." "Grove Orange" "Horizon Orange" "Peanut Corp." "Demo")
TENANT_IDS_VALUES=("7bfe6326-593d-4a47-9ba8-c882e0dd7112" "e40d082e-320d-4824-9abe-81b5ea5793e9" "c903ba11-9dc8-4317-9a20-088996a4e64f" "537b0866-2318-4ab3-bc52-c2272353777d" "007ba124-de7b-4e74-a81e-c432e8ba0e4c" "b4cd41b7-622d-4483-9ee4-8121f4089cde" "3359cf89-df37-4af8-bf30-694a3d947f81" "e24459d6-51ff-43e5-a77e-78a596dd7760" "95cf35c2-309a-4976-861b-11c7817ec668")

function get_tenant_id() {
    local TARGET="$1"
    for i in "${!TENANT_NAMES[@]}"; do
        if [[ "${TENANT_NAMES[$i]}" == "$TARGET" ]]; then
            echo "${TENANT_IDS_VALUES[$i]}"
            return
        fi
    done
    echo ""
}

# -----------------------------
# 🔹 Run Tests
# -----------------------------
PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()
SERIAL=1

echo "============================================"
echo "🌟 Multi-Tenant RBAC Test Start"
echo "============================================"

# -----------------------------
# Login Tests
# -----------------------------
echo "🔹 Running Login Tests"
for CASE in "${LOGIN_TESTS[@]}"; do
    IFS='|' read -r USER TENANT <<< "$CASE"
    if ! login "$USER"; then
        STATUS="${RED}❌${RESET}"
        ACTUAL="Login failed"
        ((FAIL_COUNT++))
    else
        STATUS="${GREEN}✅${RESET}"
        ACTUAL="Login successful"
        ((PASS_COUNT++))
    fi
    RESULTS+=("| $SERIAL | LOGIN | $USER | $TENANT | N/A | $ACTUAL | $STATUS |")
    ((SERIAL++))
done
echo "--------------------------------------------"

# -----------------------------
# 🔹 Step 2: Fetch Users Tests
# -----------------------------
echo "🔹 Running Fetch Users Tests"

for CASE in "${FETCH_USERS_TESTS[@]}"; do
    IFS='|' read -r USER TARGET_TENANT EXPECT <<< "$CASE"

    if ! login "$USER"; then
        STATUS="${RED}❌${RESET}"
        ACTUAL="Login failed"
        ((FAIL_COUNT++))
    else
        TARGET_TENANT_ID=$(get_tenant_id "$TARGET_TENANT")

        # Fetch users: separate body and HTTP code
        TMP_BODY=$(mktemp)
        HTTP_CODE=$(curl -s -o "$TMP_BODY" -w "%{http_code}" \
            -X GET "$API_URL/users/?skip=0&limit=10&tenant_id=$TARGET_TENANT_ID" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "accept: application/json")

        # Check if JSON is valid (only if status 200)
        if [[ "$HTTP_CODE" -eq 200 ]]; then
            if ! jq empty "$TMP_BODY" >/dev/null 2>&1; then
                STATUS="${RED}❌${RESET}"
                ACTUAL="Invalid JSON response"
                ((FAIL_COUNT++))
                RESULTS+=("| $SERIAL | FETCH | $USER | $TARGET_TENANT | $EXPECT | $ACTUAL | $STATUS |")
                ((SERIAL++))
                rm -f "$TMP_BODY"
                continue
            fi
        fi

        # Determine pass/fail
        if [[ "$HTTP_CODE" -eq 200 && "$EXPECT" == "pass" ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="Fetched users successfully"
            ((PASS_COUNT++))
        elif [[ "$HTTP_CODE" -eq 403 && "$EXPECT" == "fail" ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="Expected failure (403)"
            ((PASS_COUNT++))
        else
            STATUS="${RED}❌${RESET}"
            ACTUAL="Unexpected result (status: $HTTP_CODE)"
            ((FAIL_COUNT++))
        fi

        rm -f "$TMP_BODY"
    fi

    RESULTS+=("| $SERIAL | FETCH | $USER | $TARGET_TENANT | $EXPECT | $ACTUAL | $STATUS |")
    ((SERIAL++))
done
echo "--------------------------------------------"

# -----------------------------
# Create User Tests
# -----------------------------
echo "🔹 Running Create User Tests"
for CASE in "${CREATE_USER_TESTS[@]}"; do
    IFS='|' read -r USER TARGET_TENANT EXPECT <<< "$CASE"
    if ! login "$USER"; then
        STATUS="${RED}❌${RESET}"
        ACTUAL="Login failed"
        ((FAIL_COUNT++))
    else
        RANDOM_UID=$(uuidgen)
        NEW_USER_EMAIL="test_${RANDOM_UID}@example.com"
        TARGET_TENANT_ID=$(get_tenant_id "$TARGET_TENANT")
        RESULT=$(create_user "$ACCESS_TOKEN" "$TARGET_TENANT_ID" "$NEW_USER_EMAIL")
        HTTP_CODE=$(echo "$RESULT" | cut -d'|' -f1)
        BODY=$(echo "$RESULT" | cut -d'|' -f2-)

        # ✅ Pass if behavior matches expectation
        if [[ "$EXPECT" == "pass" && "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="User created"
            ((PASS_COUNT++))
        elif [[ "$EXPECT" == "fail" && "$HTTP_CODE" -ge 400 ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="Expected failure ($HTTP_CODE)"
            ((PASS_COUNT++))
        elif [[ "$EXPECT" == "integrity" && "$BODY" == *"IntegrityError"* ]]; then
            STATUS="${GREEN}✅${RESET}"
            ACTUAL="IntegrityError handled"
            ((PASS_COUNT++))
        else
            STATUS="${RED}❌${RESET}"
            ACTUAL="Did not match expected behavior ($HTTP_CODE)"
            ((FAIL_COUNT++))
        fi
    fi
    RESULTS+=("| $SERIAL | CREATE | $USER | $TARGET_TENANT | $EXPECT | $ACTUAL | $STATUS |")
    ((SERIAL++))
done
echo "--------------------------------------------"

# -----------------------------
# Print Summary
# -----------------------------
echo "============================================"
echo "🌟 Multi-Tenant RBAC Test Completed"
echo "✅ Passed: $PASS_COUNT | ❌ Failed: $FAIL_COUNT"
echo "--------------------------------------------"
echo -e "| S.No | Endpoint | User | Tenant | Expected | Actual | Status |"
echo -e "|------|---------|------|--------|---------|--------|--------|"
for LINE in "${RESULTS[@]}"; do
    echo -e "$LINE"
done
echo "============================================"
