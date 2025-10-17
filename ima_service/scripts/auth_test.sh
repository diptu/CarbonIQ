#!/usr/bin/env bash
# --------------------------------------------------------
# Multi-Tenant Authentication Test Script
# Login → Refresh → Logout (Full Test Suite)
# --------------------------------------------------------

set -uo pipefail

BASE_URL="http://127.0.0.1:8000/api/v1/auth"
LOGIN_URL="$BASE_URL/login"
REFRESH_URL="$BASE_URL/refresh"
LOGOUT_URL="$BASE_URL/logout"
PASSWORD="Hello123"

# Detect color support
if [ -t 1 ]; then
  GREEN="\033[1;32m"
  RED="\033[1;31m"
  YELLOW="\033[1;33m"
  NC="\033[0m"
else
  GREEN=""; RED=""; YELLOW=""; NC=""
fi

PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()

# -------------------------
# Generic test functions
# -------------------------
run_test() {
  case_id="$1"
  description="$2"
  email="$3"
  password="$4"
  tenant="$5"
  expected_code="$6"
  expected_result="$7"

  echo ""
  echo "----------------------------------------------------"
  echo "Test Case #$case_id: $description"
  echo "User:    $email"
  echo "Tenant:  $tenant"
  echo "Expect:  $expected_result [$expected_code]"

  response=$(curl -s -w "\n%{http_code}" -X POST "$LOGIN_URL" \
    -H "accept: application/json" \
    ${tenant:+-H "x-tenant-id: $tenant"} \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$email\", \"password\": \"$password\"}")

  body=$(echo "$response" | sed '$d')
  code=$(echo "$response" | tail -n1)

  if [ "$code" = "$expected_code" ]; then
    echo -e "Result: ${GREEN}PASS${NC} (HTTP $code)"
    RESULTS+=("$case_id|$description|$email|$tenant|PASS|$code|$body")
    PASS_COUNT=$((PASS_COUNT+1))
  else
    echo -e "Result: ${RED}FAIL${NC} (Got HTTP $code)"
    RESULTS+=("$case_id|$description|$email|$tenant|FAIL|$code|$body")
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi

  echo "Response: $body"
}

run_refresh_test() {
  case_id="$1"
  description="$2"
  refresh_token="$3"
  tenant="$4"
  expected_code="$5"
  expected_result="$6"

  echo ""
  echo "----------------------------------------------------"
  echo "Refresh Case #$case_id: $description"
  echo "Tenant:  $tenant"
  echo "Expect:  $expected_result [$expected_code]"

  response=$(curl -s -w "\n%{http_code}" -X POST "$REFRESH_URL" \
    -H "accept: application/json" \
    ${tenant:+-H "x-tenant-id: $tenant"} \
    -H "Content-Type: application/json" \
    -d "{\"refresh_token\": \"$refresh_token\"}")

  body=$(echo "$response" | sed '$d')
  code=$(echo "$response" | tail -n1)

  if [ "$code" = "$expected_code" ]; then
    echo -e "Result: ${GREEN}PASS${NC} (HTTP $code)"
    RESULTS+=("$case_id|$description|refresh|$tenant|PASS|$code|$body")
    PASS_COUNT=$((PASS_COUNT+1))
  else
    echo -e "Result: ${RED}FAIL${NC} (Got HTTP $code)"
    RESULTS+=("$case_id|$description|refresh|$tenant|FAIL|$code|$body")
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi

  echo "Response: $body"
}

run_logout_test() {
  case_id="$1"
  description="$2"
  access_token="$3"
  refresh_token="$4"
  expected_code="$5"
  expected_result="$6"

  echo ""
  echo "----------------------------------------------------"
  echo "Logout Case #$case_id: $description"
  echo "Expect:  $expected_result [$expected_code]"

  response=$(curl -s -w "\n%{http_code}" -X POST "$LOGOUT_URL" \
    -H "accept: application/json" \
    -H "Authorization: Bearer $access_token" \
    ${refresh_token:+-G --data-urlencode "refresh_token=$refresh_token"} )

  body=$(echo "$response" | sed '$d')
  code=$(echo "$response" | tail -n1)

  if [ "$code" = "$expected_code" ]; then
    echo -e "Result: ${GREEN}PASS${NC} (HTTP $code)"
    RESULTS+=("$case_id|$description|logout|N/A|PASS|$code|$body")
    PASS_COUNT=$((PASS_COUNT+1))
  else
    echo -e "Result: ${RED}FAIL${NC} (Got HTTP $code)"
    RESULTS+=("$case_id|$description|logout|N/A|FAIL|$code|$body")
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi

  echo "Response: $body"
}

# -------------------------
# LOGIN TEST CASES
# -------------------------
run_test 1 "Admin can log in" "admin@apple.com" "$PASSWORD" "apple.company" 200 "Success"
run_test 2 "Billing user login" "billing@orchard.apple.com" "$PASSWORD" "orchard.apple.company" 200 "Success"
run_test 3 "Admin logs into own tenant" "admin@orange.com" "$PASSWORD" "orange.company" 200 "Success"
run_test 4 "Basic-plan admin login" "admin@peanut.com" "$PASSWORD" "peanut.company" 200 "Success"
run_test 5 "Admin cannot log in to non-existent tenant" "admin@mango.com" "$PASSWORD" "nonexistent.company" 403 "Fail"
run_test 6 "Authentication fails with wrong password" "admin@apple.com" "WrongPass" "apple.company" 401 "Fail"
run_test 7 "Inactive users denied" "inactive@apple.com" "$PASSWORD" "apple.company" 403 "Fail"
run_test 8 "Admin login to child tenant" "admin@apple.com" "$PASSWORD" "orchard.apple.company" 200 "Success"
run_test 9 "Admin login to unrelated tenant" "admin@apple.com" "$PASSWORD" "orange.company" 403 "Fail"
run_test 10 "Regular user cannot login to parent tenant" "billing@orchard.apple.com" "$PASSWORD" "apple.company" 403 "Fail"
run_test 11 "Super-admin login to any tenant" "admin@carboniq.com" "$PASSWORD" "orange.company" 200 "Success"
run_test 12 "Super-admin login without tenant header" "admin@carboniq.com" "$PASSWORD" "" 200 "Success"
run_test 13 "Login without tenant header (non-super-admin)" "admin@apple.com" "$PASSWORD" "" 403 "Fail"

# -------------------------
# REFRESH TOKEN TEST CASES
# -------------------------
REFRESH_TOKEN_APPLE=$(curl -s -X POST "$LOGIN_URL" \
  -H "accept: application/json" \
  -H "x-tenant-id: apple.company" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@apple.com\", \"password\": \"$PASSWORD\"}" | jq -r '.data.refresh_token')

NEW_REFRESH_TOKEN=$(curl -s -X POST "$LOGIN_URL" \
  -H "accept: application/json" \
  -H "x-tenant-id: apple.company" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@apple.com\", \"password\": \"$PASSWORD\"}" | jq -r '.data.refresh_token')

run_refresh_test 14 "Refresh token with valid token" "$REFRESH_TOKEN_APPLE" "apple.company" 200 "Success"
run_refresh_test 15 "Refresh token with invalid token" "invalid.token.value" "apple.company" 401 "Fail"
run_refresh_test 16 "Refresh token from wrong tenant" "$REFRESH_TOKEN_APPLE" "orange.company" 403 "Fail"
REVOKED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
run_refresh_test 17 "Refresh with manually revoked token" "$REVOKED_TOKEN" "apple.company" 401 "Fail"
run_refresh_test 18a "Valid rotation refresh (new token)" "$NEW_REFRESH_TOKEN" "apple.company" 200 "Success"
run_refresh_test 18b "Reuse old refresh token after rotation" "$REFRESH_TOKEN_APPLE" "apple.company" 401 "Fail"

# -------------------------
# LOGOUT TEST CASES
# -------------------------
LOGIN_RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
  -H "accept: application/json" \
  -H "x-tenant-id: apple.company" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@apple.com\", \"password\": \"$PASSWORD\"}")

ACCESS_TOKEN_APPLE=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token')
REFRESH_TOKEN_APPLE=$(echo "$LOGIN_RESPONSE" | jq -r '.data.refresh_token')

run_logout_test 19a "Logout a single refresh token" "$ACCESS_TOKEN_APPLE" "$REFRESH_TOKEN_APPLE" 200 "Success"
run_logout_test 19b "Logout all refresh tokens for user" "$ACCESS_TOKEN_APPLE" "" 200 "Success"
run_logout_test 19c "Logout with invalid access token" "invalid.access.token" "$REFRESH_TOKEN_APPLE" 401 "Fail"

# -------------------------
# SUMMARY
# -------------------------
echo ""
echo "===================================================="
echo -e "${YELLOW}Test Summary${NC}"
echo "===================================================="
printf "%-3s | %-35s | %-25s | %-22s | %-6s | %-5s\n" "#" "Description" "User/Action" "Tenant" "Result" "HTTP"
echo "------------------------------------------------------------------------------------------------------------"
for result in "${RESULTS[@]}"; do
  IFS="|" read -r id desc action tenant status code body <<< "$result"
  if [ "$status" = "PASS" ]; then color="$GREEN"; else color="$RED"; fi
  printf "%-3s | %-35s | %-25s | %-22s | ${color}%-6s${NC} | %-5s\n" "$id" "$desc" "$action" "$tenant" "$status" "$code"
done
echo "------------------------------------------------------------------------------------------------------------"
echo -e "✅ Passed: ${GREEN}$PASS_COUNT${NC}   ❌ Failed: ${RED}$FAIL_COUNT${NC}"
echo "===================================================="
