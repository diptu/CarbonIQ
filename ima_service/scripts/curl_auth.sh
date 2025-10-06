#!/bin/bash
# --------------------------------------------
# Auto-login and call /api/v1/users/
# --------------------------------------------

BASE_URL="http://0.0.0.0:8000"
USERNAME="tenant_admin@carboniq.com"
PASSWORD="Hello123"

# Helper function to print JSON nicely
print_json() {
    echo "$1" | python3 -m json.tool || echo "$1"
}

# Step 1: Login and get access token
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('accessToken', ''))")

if [ -z "$TOKEN" ]; then
  echo "Failed to get access token. Response:"
  print_json "$RESPONSE"
  exit 1
fi

echo "Access token fetched successfully!"

# Step 2: Call /api/v1/users/ (try both with and without trailing slash)
for endpoint in "/api/v1/users/" "/api/v1/users"; do
  echo "Trying endpoint: $endpoint"
  HTTP_RESPONSE=$(curl -s -X GET "$BASE_URL$endpoint" \
    -H "accept: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -w "\nHTTP_STATUS:%{http_code}")

  HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed -n '1h;2,$H;$!d;${g;p;}')
  HTTP_STATUS=$(echo "$HTTP_RESPONSE" | tr -d '\n' | sed -n 's/.*HTTP_STATUS://p')

  if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Request successful!"
    print_json "$HTTP_BODY"
    exit 0
  else
    echo "Request failed with status $HTTP_STATUS"
    echo "Response body:"
    print_json "$HTTP_BODY"
  fi
done

echo "All attempts failed."
exit 1
