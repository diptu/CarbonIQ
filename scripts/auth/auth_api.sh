#!/bin/bash

AUTH_URL="http://localhost:8002"
USER_URL="http://3.25.65.83:8000"
EMAIL="admin@apple.com"
PASSWORD="Hello123"

echo "=== LOGIN ==="
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" || -z "$REFRESH_TOKEN" ]]; then
  echo "❌ Login failed — missing tokens, aborting."
  exit 1
fi

AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"

echo
echo "=== REFRESH TOKEN ==="
REFRESH_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo "$REFRESH_RESPONSE" | jq .

NEW_REFRESH_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$NEW_REFRESH_TOKEN" ]]; then
  echo "❌ Refresh failed — cannot continue to logout."
  exit 1
fi

echo
echo "=== LOGOUT ==="
LOGOUT_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/logout" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "$LOGOUT_RESPONSE" | jq .

BLACKLISTED=$(echo "$LOGOUT_RESPONSE" | jq -r '.detail // empty')
if [[ "$BLACKLISTED" == *"already blacklisted"* ]]; then
  echo "✔ Token already blacklisted."
  exit 0
fi

echo
echo "=== ATTEMPT REFRESH AFTER LOGOUT ==="
POST_LOGOUT_REFRESH=$(curl -s -X POST "$AUTH_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "$POST_LOGOUT_REFRESH" | jq .
