#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# 🔑 Login Function
# -----------------------------
function login() {
    local EMAIL="$1"
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "accept: application/json" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=$EMAIL&password=$PASSWORD")

    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.details.accessToken // empty')
    TENANT_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.details.tenantId // empty')

    if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
        echo "❌ Login failed for $EMAIL"
        return 1
    fi
    echo "✅ Logged in: $EMAIL | Tenant ID: $TENANT_ID"
    return 0
}

# -----------------------------
# 📋 Fetch Users
# -----------------------------
function fetch_users() {
    local TOKEN="$1"
    curl -s -X GET "$API_URL/users/?skip=0&limit=10" \
        -H "Authorization: Bearer $TOKEN" \
        -H "accept: application/json"
}

# -----------------------------
# # 👤 Create User with Tenant Validation
# -----------------------------

function create_user() {
    local TOKEN="$1"
    local TARGET_TENANT="$2"
    local EMAIL="$3"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/?tenant_id=$TARGET_TENANT" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$EMAIL\",
            \"password\": \"$PASSWORD\"
        }")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    # Explicitly detect forbidden creation
    if [[ "$HTTP_CODE" -eq 403 ]]; then
        echo "403|Forbidden: Cannot create user in unrelated tenant"
        return
    fi

    echo "$HTTP_CODE|$BODY"
}
