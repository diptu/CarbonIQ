#!/bin/bash

API_URL="http://127.0.0.1:8000/api/v1"
EMAIL="admin@carboniq.com"
PASSWORD="Hello123"

echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -F "email=$EMAIL" \
  -F "password=$PASSWORD")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.details.accessToken' 2>/dev/null)

if [[ "$ACCESS_TOKEN" == "null" || -z "$ACCESS_TOKEN" ]]; then
  echo "Login failed. Response:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "Login successful. Access token retrieved."
echo "Fetching users..."

USERS_RESPONSE=$(curl -s -X GET "$API_URL/users/?skip=0&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json")

# Print raw response for debugging
echo "Raw users response:"
echo "$USERS_RESPONSE"

# Attempt to parse JSON if possible
echo "$USERS_RESPONSE" | jq . 2>/dev/null || echo "Response is not valid JSON."
