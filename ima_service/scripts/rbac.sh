#!/usr/bin/env bash
set -euo pipefail

API_URL="http://127.0.0.1:8000/api/v1"
PASSWORD="Hello123"

# -----------------------------
# ✅ Helper Functions
# -----------------------------
function login() {
    local EMAIL="$1"
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "accept: application/json" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=$EMAIL&password=$PASSWORD")
    
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.details.accessToken // empty' 2>/dev/null)
    TENANT_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.details.tenantId // empty' 2>/dev/null)
    
    if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
        echo "❌ Login failed for $EMAIL"
        return 1
    fi
    echo "✅ Logged in: $EMAIL | Tenant ID: $TENANT_ID"
    return 0
}

function fetch_users() {
    local TOKEN="$1"
    curl -s -X GET "$API_URL/users/?skip=0&limit=10" \
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
# 🌱 Define Test Cases
# -----------------------------
TEST_CASES=(
"1|admin@apple.com|Apple Inc.|pass"
"2|admin@apple.com|Orchard Apple|pass"
"3|admin@apple.com|Orange Ltd.|fail"
"4|billing@orchard.apple.com|Orchard Apple|pass"
"5|billing@orchard.apple.com|Apple Inc.|fail"
"6|billing@orchard.apple.com|Orchard Apple|integrity"
"7|admin@orange.com|Grove Orange|pass"
"8|admin@peanut.com|Peanut Corp.|pass"
"9|admin@peanut.com|NonExistent|fail"
)

# -----------------------------
# 🔹 Run Test Cases & Capture Results
# -----------------------------
PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()  # Store summary lines

echo "============================================"
echo "🌟 Multi-Tenant RBAC Test Start"
echo "============================================"

for CASE in "${TEST_CASES[@]}"; do
    IFS='|' read -r ID USER TARGET_TENANT EXPECT <<< "$CASE"
    echo "🔑 Test #$ID | User: $USER | Tenant: $TARGET_TENANT | Expected: $EXPECT"

    if ! login "$USER"; then
        STATUS="❌"
        ACTUAL="Login failed"
        ((FAIL_COUNT++))
        RESULTS+=("| $ID | $USER | $TARGET_TENANT | $EXPECT | $ACTUAL | $STATUS |")
        echo "--------------------------------------------"
        continue
    fi

    if [[ "$ID" == "4" || "$ID" == "5" ]]; then
        USERS_JSON=$(fetch_users "$ACCESS_TOKEN")
        STATUS_CODE=$(echo "$USERS_JSON" | jq -r '.statusCode // empty')
        if [[ "$EXPECT" == "pass" && "$STATUS_CODE" == "200" ]]; then
            STATUS="✅"
            ACTUAL="Fetched users successfully"
            ((PASS_COUNT++))
        else
            STATUS="❌"
            ACTUAL="Fetch failed"
            ((FAIL_COUNT++))
        fi
    else
        RANDOM_UID=$(uuidgen)
        NEW_USER_EMAIL="test_${RANDOM_UID}@example.com"
        RESULT=$(create_user "$ACCESS_TOKEN" "$TENANT_ID" "$NEW_USER_EMAIL")
        HTTP_CODE=$(echo "$RESULT" | cut -d'|' -f1)
        BODY=$(echo "$RESULT" | cut -d'|' -f2-)

        if [[ "$EXPECT" == "pass" && "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
            STATUS="✅"
            ACTUAL="User created"
            ((PASS_COUNT++))
        elif [[ "$EXPECT" == "fail" && "$HTTP_CODE" -eq 403 ]]; then
            STATUS="✅"
            ACTUAL="Expected failure (403)"
            ((PASS_COUNT++))
        elif [[ "$EXPECT" == "integrity" && "$HTTP_CODE" -eq 500 && "$BODY" == *"IntegrityError"* ]]; then
            STATUS="✅"
            ACTUAL="IntegrityError handled"
            ((PASS_COUNT++))
        else
            STATUS="❌"
            ACTUAL="User created (unexpected)"
            ((FAIL_COUNT++))
        fi
    fi

    RESULTS+=("| $ID | $USER | $TARGET_TENANT | $EXPECT | $ACTUAL | $STATUS |")
    echo "--------------------------------------------"
done

# -----------------------------
# 🔹 Print Clean Summary Table
# -----------------------------
echo "============================================"
echo "🌟 Multi-Tenant RBAC Test Completed"
echo "✅ Passed: $PASS_COUNT | ❌ Failed: $FAIL_COUNT"
echo "--------------------------------------------"
echo "| ID | User | Tenant | Expected | Actual | Status |"
echo "|----|------|--------|---------|--------|--------|"
for LINE in "${RESULTS[@]}"; do
    echo "$LINE"
done
echo "============================================"
