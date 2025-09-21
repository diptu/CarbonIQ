#!/usr/bin/env bash
# Minimal sanity suite for IMA (health + users).
# Usage:
#   ./scripts/sanity.sh [BASE_URL] [STRICT]
# Env:
#   BASE_URL, STRICT, REQUIRE_REDIS (env vars override args)

set -u
BASE="${BASE_URL:-${1:-http://127.0.0.1:8000/api/v1}}"
STRICT="${STRICT:-${2:-0}}"
REQUIRE_REDIS="${REQUIRE_REDIS:-0}"
TIMEOUT="${IMA_TIMEOUT:-3}"

# colors
C_G="\033[32m"; C_Y="\033[33m"; C_R="\033[31m"; C_X="\033[0m"
PASS=0; WARN=0; FAIL=0
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT

say()  { printf "%b\n" "$*"; }
ok()   { say "${C_G}✅$C_X $*"; PASS=$((PASS+1)); }
warn() { say "${C_Y}⚠️ $C_X $*"; WARN=$((WARN+1)); }
bad()  { say "${C_R}❌$C_X $*"; FAIL=$((FAIL+1)); }

curlj() {
  local method; method="$1"
  local path;   path="$2"
  local data;   data="${3:-}"
  local url;    url="${BASE}${path}"
  local http
  if [ -n "$data" ]; then
    http=$(curl -sS -m "$TIMEOUT" -w "%{http_code}" \
      -H 'accept: application/json' -H 'content-type: application/json' \
      -o "$tmp" -X "$method" "$url" -d "$data" || echo 000)
  else
    http=$(curl -sS -m "$TIMEOUT" -w "%{http_code}" \
      -H 'accept: application/json' -o "$tmp" -X "$method" "$url" || echo 000)
  fi
  echo "$http"
}

body() { cat "$tmp"; }
j()    { jq -r "$1" <"$tmp" 2>/dev/null; }

say "Running sanity against ${BASE} (strict=${STRICT}, "\
"require_redis=${REQUIRE_REDIS})"

# ------------ health: server ------------
http=$(curlj GET /health/server)
if [ "$http" = "200" ]; then ok "GET /health/server -> 200"
else bad "GET /health/server -> $http"; body; fi

# ------------ health: db ------------
http=$(curlj GET /health/database)
if [ "$http" = "200" ]; then ok "GET /health/database -> 200"
else bad "GET /health/database -> $http"; body; fi

# ------------ health: redis ------------
http=$(curlj GET /health/redis)
code=$(j '.code // empty')
status=$(j '.data.status // .status // empty')

if [ "$http" = "200" ]; then
  if [ "$REQUIRE_REDIS" = "1" ] && [ "$status" != "ok" ]; then
    bad "GET /health/redis -> 200 but status=$status (required)"
  else
    ok "GET /health/redis -> 200 ($status)"
  fi
elif [ "$http" = "503" ] && [ "$code" = "REDIS_DOWN" ]; then
  if [ "$STRICT" = "1" ] || [ "$REQUIRE_REDIS" = "1" ]; then
    bad "GET /health/redis -> 503 ($code)"
  else
    warn "GET /health/redis -> 503 ($code)"
  fi
else
  bad "GET /health/redis -> $http"; body
fi

# ------------ health: aggregate ------------
http=$(curlj GET /health)
code=$(j '.code // empty')
agg_status=$(j '.data.status // .status // empty')
redis_status=$(j '.data.redis.status // empty')

if [ "$http" = "200" ]; then
  ok "GET /health -> 200"
elif [ "$http" = "503" ] && [ "$code" = "SERVICE_DEGRADED" ]; then
  if [ "$STRICT" = "1" ] || { [ "$REQUIRE_REDIS" = "1" ] \
       && [ "$redis_status" != "ok" ]; }; then
    bad "GET /health -> 503 ($code, redis=$redis_status)"
  else
    warn "GET /health -> 503 ($code)"
  fi
else
  bad "GET /health -> $http"; body
fi

# ------------ users flow ------------
# robust unique email (works on macOS/Linux)
uuid_val="$(python - <<'PY'
import uuid; print(uuid.uuid4())
PY
)"
email="sanity-${uuid_val}@example.com"
name="Sanity User"
passw="S@nity1234"
payload=$(jq -n --arg e "$email" --arg n "$name" --arg p "$passw" \
  '{email:$e, name:$n, password:$p, role:"viewer"}')

http=$(curlj POST /users "$payload")
if [ "$http" = "201" ]; then
  uid=$(j '.data.id')
  [ -n "$uid" ] && ok "POST /users -> 201 (id=$uid)" \
                || { bad "POST /users -> 201 but id missing"; body; }
elif [ "$http" = "409" ] && [ "$(j .code)" = "USER_EMAIL_EXISTS" ]; then
  bad "POST /users -> 409 email exists (unexpected)"
  body
else
  bad "POST /users -> $http"; body
fi

if [ -n "${uid:-}" ]; then
  http=$(curlj GET "/users/${uid}")
  if [ "$http" = "200" ] && [ "$(j '.data.id')" = "$uid" ]; then
    ok "GET /users/{id} -> 200"
  else
    bad "GET /users/{id} -> $http"; body
  fi
fi

http=$(curlj GET "/users?role=viewer")
total=$(j '.data.total // 0')
if [ "$http" = "200" ] && [ "$total" -ge 1 ]; then
  ok "GET /users?role=viewer -> 200 (total=$total)"
else
  bad "GET /users?role=viewer -> $http"; body
fi

http=$(curlj POST "/users/login?email=${email}&password=${passw}")
acc=$(j '.data.access // empty'); ref=$(j '.data.refresh // empty')
if [ "$http" = "200" ] && [ -n "$acc" ] && [ -n "$ref" ]; then
  ok "POST /users/login -> 200 (tokens ok)"
elif [ "$http" = "401" ]; then
  bad "POST /users/login -> 401 (invalid creds)"; body
else
  bad "POST /users/login -> $http"; body
fi

# ------------ summary ------------
say ""
say "Summary: ${C_G}${PASS} pass${C_X}, ${C_Y}${WARN} warn${C_X}, "\
"${C_R}${FAIL} fail${C_X}"
[ "$FAIL" -eq 0 ] || exit 1
