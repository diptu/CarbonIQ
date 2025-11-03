#!/bin/bash

AUTH_URL="http://localhost:8001"
USER_URL="http://localhost:8000"
EMAIL="admin@carboniq.com"
PASSWORD="Hello123"

echo "=== LOGIN ==="
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" || -z "$REFRESH_TOKEN" ]]; then
  echo "Login failed, aborting further steps."
  exit 1
fi

echo
echo "=== LIST USERS (AFTER LOGIN) ==="
USERS_RESPONSE=$(curl -s -X GET "$USER_URL/users/?skip=0&limit=100" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

# Try parsing JSON, fallback to raw if error
echo "$USERS_RESPONSE" | jq . 2>/dev/null || echo "Raw response: $USERS_RESPONSE"


# echo
# echo "=== REFRESH TOKEN ==="
# REFRESH_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/refresh" \
#   -H "Content-Type: application/json" \
#   -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

# echo "$REFRESH_RESPONSE" | jq .

# NEW_REFRESH_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.data.refresh_token // empty')

# if [[ -z "$NEW_REFRESH_TOKEN" ]]; then
#   echo "Refresh failed, aborting logout step."
#   exit 1
# fi

# echo
# echo "=== LOGOUT ==="
# LOGOUT_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/logout" \
#   -H "Content-Type: application/json" \
#   -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

# echo "$LOGOUT_RESPONSE" | jq .

# # Check if the token is blacklisted
# BLACKLISTED=$(echo "$LOGOUT_RESPONSE" | jq -r '.detail // empty')
# if [[ "$BLACKLISTED" == *"already blacklisted"* ]]; then
#   echo "Token is already blacklisted. No further refresh allowed."
#   exit 0
# fi

# echo
# echo "=== ATTEMPT REFRESH AFTER LOGOUT ==="
# POST_LOGOUT_REFRESH=$(curl -s -X POST "$AUTH_URL/auth/refresh" \
#   -H "Content-Type: application/json" \
#   -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

# echo "$POST_LOGOUT_REFRESH" | jq .
