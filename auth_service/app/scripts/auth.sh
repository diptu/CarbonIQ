#!/bin/bash

BASE_URL="http://localhost:8001"
EMAIL="admin@carboniq.com"
PASSWORD="Hello123"

echo "=== LOGIN ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" || -z "$REFRESH_TOKEN" ]]; then
  echo "Login failed, aborting refresh/logout steps."
  exit 1
fi

echo
echo "=== REFRESH TOKEN ==="
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo "$REFRESH_RESPONSE" | jq .

NEW_REFRESH_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.data.refresh_token // empty')

if [[ -z "$NEW_REFRESH_TOKEN" ]]; then
  echo "Refresh failed, aborting logout step."
  exit 1
fi

echo
echo "=== LOGOUT ==="
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/logout" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "$LOGOUT_RESPONSE" | jq .

# Check if the token is blacklisted
BLACKLISTED=$(echo "$LOGOUT_RESPONSE" | jq -r '.detail // empty')

if [[ "$BLACKLISTED" == *"already blacklisted"* ]]; then
  echo "Token is already blacklisted. No further refresh allowed."
  exit 0
fi

echo
echo "=== ATTEMPT REFRESH AFTER LOGOUT ==="
POST_LOGOUT_REFRESH=$(curl -s -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$NEW_REFRESH_TOKEN\"}")

echo "$POST_LOGOUT_REFRESH" | jq .
