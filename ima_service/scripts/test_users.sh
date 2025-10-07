#!/bin/bash

API_URL="http://127.0.0.1:8000/api/v1"
EMAIL="admin@apple.com"
PASSWORD="Hello123"

# -----------------------------
# 🔐 Login and get access token
# -----------------------------
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -F "email=$EMAIL" \
  -F "password=$PASSWORD")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.details.accessToken' 2>/dev/null)
DEFAULT_TENANT_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.details.tenantId' 2>/dev/null)

if [[ "$ACCESS_TOKEN" == "null" || -z "$ACCESS_TOKEN" ]]; then
  echo "Login failed. Response:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "Login successful. Access token retrieved. Default tenant ID: $DEFAULT_TENANT_ID"

# -----------------------------
# 📋 Fetch users
# -----------------------------
echo "Fetching users..."
USERS_RESPONSE=$(curl -s -X GET "$API_URL/users/?skip=0&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

echo "Raw users response:"
echo "$USERS_RESPONSE"
echo "$USERS_RESPONSE" | jq . 2>/dev/null || echo "Response is not valid JSON."

# -----------------------------
# 🧩 Create new user
# -----------------------------
# Generate random UID-based email
RANDOM_UID=$(uuidgen)
NEW_USER_EMAIL="user_${RANDOM_UID}@example.com"
NEW_USER_PASSWORD="Password123"

# Optional: specify child tenantId here
CHILD_TENANT_ID=""  # leave empty if you want to use default parent tenant

# Use child tenant if provided, else fallback to default parent tenant
TENANT_ID_TO_USE=${CHILD_TENANT_ID:-$DEFAULT_TENANT_ID}

echo "Creating new user: $NEW_USER_EMAIL under tenant $TENANT_ID_TO_USE ..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/users/?tenant_id=$TENANT_ID_TO_USE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$NEW_USER_EMAIL\",
    \"password\": \"$NEW_USER_PASSWORD\"
  }")

echo "Raw create user response:"
echo "$CREATE_RESPONSE"
echo "$CREATE_RESPONSE" | jq . 2>/dev/null || echo "Response is not valid JSON."
