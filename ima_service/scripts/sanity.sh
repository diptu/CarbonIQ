# FILE: ima_service/scripts/sanity.sh
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

load_dotenv() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  # shellcheck disable=SC1090
  set -a; . "$f"; set +a
}
load_dotenv "${SCRIPT_DIR}/../../.env"  # repo root
load_dotenv "${SCRIPT_DIR}/../.env"     # service root
load_dotenv ".env"                      # cwd

# Derive BASE_URL via settings if not provided
if [[ -z "${BASE_URL:-}" ]] && command -v python >/dev/null 2>&1; then
  BASE_URL="$(python - <<'PY' || true
try:
    from urllib.parse import urlparse
    try:
        from ima_service.app.core import get_settings  # type: ignore
    except Exception:
        from ima_service.app.core.config import get_settings  # type: ignore
    s = get_settings()
    u = urlparse(s.base_url)
    scheme = u.scheme or "http"
    host = u.hostname or (u.netloc or u.path or "127.0.0.1")
    port = getattr(s, "port", None) or (u.port or 8000)
    print(f"{scheme}://{host}:{port}")
except Exception:
    pass
PY
)"
fi

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

# API prefix (default /v1). Set API_PREFIX="" if mounted at root.
API_PREFIX="${API_PREFIX:-/v1}"
[[ -n "$API_PREFIX" && "${API_PREFIX:0:1}" != "/" ]] && API_PREFIX="/$API_PREFIX"

TIMEOUT="${TIMEOUT:-3}"
RETRIES="${RETRIES:-2}"
SANITY_STRICT="${SANITY_STRICT:-0}"   # 1 = all OK required
SANITY_TRACE="${SANITY_TRACE:-0}"     # 1 = print headers/body

has_jq() { command -v jq >/dev/null 2>&1; }
JQ_AVAILABLE="true"
if ! has_jq; then
  JQ_AVAILABLE="false"
  echo 'WARN: jq not found; JSON assertions skipped and User API tests disabled.' >&2
fi

ok()   { printf '✅ %s\n' "$*"; }
warn() { printf '⚠️  %s\n' "$*"; }
bad()  { printf '❌ %s\n' "$*"; }
log()  { printf '%s\n' "$*" >&2; }

curl_request() {
  local method="$1" url="$2" body_file="$3" hdr_file="$4"
  curl -sS \
       --max-time "$TIMEOUT" \
       --connect-timeout "$TIMEOUT" \
       --retry "$RETRIES" --retry-all-errors \
       -X "$method" "$url" \
       -D "$hdr_file" \
       --output "$body_file" \
       --write-out '%{http_code}'
}

# JSON request helper (adds content-type + raw JSON string body)
curl_request_json() {
  local method="$1" url="$2" json_str="$3" body_file="$4" hdr_file="$5"
  curl -sS \
       --max-time "$TIMEOUT" \
       --connect-timeout "$TIMEOUT" \
       --retry "$RETRIES" --retry-all-errors \
       -X "$method" "$url" \
       -H 'Content-Type: application/json' \
       --data "$json_str" \
       -D "$hdr_file" \
       --output "$body_file" \
       --write-out '%{http_code}'
}

assert_json() {
  local body="$1" key="$2" expected="$3"
  [[ "$JQ_AVAILABLE" != "true" ]] && return 0
  jq -e --arg exp "$expected" ".${key} == \$exp" <"$body" >/dev/null
}

classify_http() {
  local got="$1" expect="$2"
  CLASS="fail"
  if [[ "$expect" == *"|"* ]]; then
    local oldifs="$IFS"; IFS='|' read -r -a opts <<<"$expect"; IFS="$oldifs"
    if [[ "$got" == "${opts[0]}" ]]; then CLASS="pass"; return 0; fi
    for opt in "${opts[@]:1}"; do
      [[ "$got" == "$opt" ]] && { CLASS="warn"; return 0; }
    done
    CLASS="fail"; return 0
  else
    [[ "$got" == "$expect" ]] && CLASS="pass" || CLASS="fail"
  fi
}

check_status_matches_json_code() {
  local http="$1" body="$2"
  [[ "$JQ_AVAILABLE" != "true" ]] && return 0
  local jcode
  jcode="$(jq -r '.code // empty' <"$body" || true)"
  [[ -z "$jcode" ]] && return 0
  [[ "$jcode" == "$http" ]]
}

run_check() {
  local method="$1" path="$2" expect="$3"; shift 3
  local url="${BASE_URL%/}${API_PREFIX%/}${path}"
  local body hdr http
  body="$(mktemp)"; hdr="$(mktemp)"
  http="$(curl_request "$method" "$url" "$body" "$hdr" || true)"

  if [[ "$SANITY_TRACE" == "1" ]]; then
    echo "--- TRACE $method $url ---" >&2
    echo "[HTTP $http]" >&2
    sed -n '1,20p' "$hdr" >&2
    echo "--- BODY ---" >&2; head -c 400 "$body" >&2; echo >&2
    echo "------------" >&2
  fi

  classify_http "$http" "$expect"

  if ! check_status_matches_json_code "$http" "$body"; then
    bad "$method $path: HTTP $http != JSON .code"
    [[ -s "$body" ]] && log "Body: $(head -c 300 "$body")"
    rm -f "$body" "$hdr"; return 2
  fi

  case "$CLASS" in
    pass)
      local kv k v
      for kv in "$@"; do
        k="${kv%%=*}"; v="${kv#*=}"
        if ! assert_json "$body" "$k" "$v"; then
          bad "$method $path JSON: $k != $v"
          [[ -s "$body" ]] && log "Body: $(head -c 300 "$body")"
          rm -f "$body" "$hdr"; return 2
        fi
      done
      ok "$method $path -> $http OK"
      ;;
    warn)
      warn "$method $path -> $http Degraded (accepted)"
      ;;
    *)
      bad "$method $path -> $http (expected $expect)"
      [[ -s "$body" ]] && log "Body: $(head -c 300 "$body")"
      rm -f "$body" "$hdr"; return 2
      ;;
  esac

  rm -f "$body" "$hdr"; return 0
}

build_checks() {
  CHECKS=(
    'GET /health/server 200 status=success data.status=ok'
    'GET /health/database 200'
    'GET /health/redis 200'
  )
  if [[ "$SANITY_STRICT" == "1" ]]; then
    CHECKS+=('GET /health/ 200 status=success data.status=ok')
  else
    CHECKS+=('GET /health/ 200|503')
  fi
}

# ------------------------------
# User API sanity flow (requires jq)
# ------------------------------
run_user_flow() {
  [[ "$JQ_AVAILABLE" != "true" ]] && { warn "Skipping User API tests (jq not available)"; return 0; }

  local url body hdr http uid email pass uname1 uname2
  body="$(mktemp)"; hdr="$(mktemp)"

  # Generate unique credentials (sanitize to ^[a-zA-Z0-9_.]{3,32}$)
  local nonce raw_uname
  nonce="$(date +%s)$$"                # numeric-only, no hyphen
  raw_uname="sanity_${nonce}"
  sanitize_uname() { echo "$1" | tr -cd '[:alnum:]_.' | cut -c1-32; }

  email="${SANITY_USER_EMAIL:-sanity-${nonce}@example.com}"
  pass="${SANITY_USER_PASSWORD:-S@nityP4ssw0rd!}"
  uname1="${SANITY_USER_USERNAME:-$(sanitize_uname "$raw_uname")}"
  uname2="${SANITY_USER_USERNAME2:-$(sanitize_uname "${raw_uname}_v2")}"

  # 1) Create user: POST /users
  url="${BASE_URL%/}${API_PREFIX%/}/users"
  local create_json
  create_json="$(jq -nc --arg e "$email" --arg p "$pass" --arg u "$uname1" \
      '{email:$e, password:$p, username:$u}')"

  http="$(curl_request_json POST "$url" "$create_json" "$body" "$hdr" || true)"
  if [[ "$SANITY_TRACE" == "1" ]]; then
    echo "--- TRACE POST $url ---" >&2
    echo "[HTTP $http]" >&2
    sed -n '1,20p' "$hdr" >&2
    echo "--- BODY ---" >&2; cat "$body" >&2; echo >&2
    echo "------------" >&2
  fi
  if [[ "$http" != "201" ]]; then
    bad "POST /users -> $http (expected 201)"
    [[ -s "$body" ]] && log "Body: $(head -c 400 "$body")"
    rm -f "$body" "$hdr"; return 2
  fi

  uid="$(jq -r '.id // empty' <"$body")"
  if [[ -z "$uid" || "$uid" == "null" ]]; then
    bad "POST /users did not return .id"
    log "Body: $(head -c 400 "$body")"
    rm -f "$body" "$hdr"; return 2
  fi
  ok "POST /users -> 201 (id=$uid)"

  # 2) Get user: GET /users/{id}
  : >"$body"; : >"$hdr"
  url="${BASE_URL%/}${API_PREFIX%/}/users/${uid}"
  http="$(curl_request GET "$url" "$body" "$hdr" || true)"
  if [[ "$http" != "200" ]]; then
    bad "GET /users/${uid} -> $http (expected 200)"; rm -f "$body" "$hdr"; return 2
  fi
  if ! assert_json "$body" "email" "$email"; then
    bad "GET /users/${uid} JSON mismatch: email"
    log "Body: $(head -c 400 "$body")"; rm -f "$body" "$hdr"; return 2
  fi
  ok "GET /users/${uid} -> 200"

  # 3) Patch username: PATCH /users/{id}
  : >"$body"; : >"$hdr"
  url="${BASE_URL%/}${API_PREFIX%/}/users/${uid}"
  local patch_json
  patch_json="$(jq -nc --arg u "$uname2" '{username:$u}')"
  http="$(curl_request_json PATCH "$url" "$patch_json" "$body" "$hdr" || true)"
  if [[ "$http" != "200" ]]; then
    bad "PATCH /users/${uid} -> $http (expected 200)"; rm -f "$body" "$hdr"; return 2
  fi
  if ! assert_json "$body" "username" "$uname2"; then
    bad "PATCH /users/${uid} JSON mismatch: username"
    log "Body: $(head -c 400 "$body")"; rm -f "$body" "$hdr"; return 2
  fi
  ok "PATCH /users/${uid} -> 200"

  # 4) Deactivate: POST /users/{id}/deactivate  (204 no body)
  : >"$body"; : >"$hdr"
  url="${BASE_URL%/}${API_PREFIX%/}/users/${uid}/deactivate"
  http="$(curl_request POST "$url" "$body" "$hdr" || true)"
  if [[ "$http" != "204" ]]; then
    bad "POST /users/${uid}/deactivate -> $http (expected 204)"
    [[ -s "$body" ]] && log "Body: $(head -c 400 "$body")"
    rm -f "$body" "$hdr"; return 2
  fi
  ok "POST /users/${uid}/deactivate -> 204"

  rm -f "$body" "$hdr"; return 0
}

main() {
  build_checks
  printf 'Running sanity checks against %s%s (strict=%s)\n' \
         "$BASE_URL" "$API_PREFIX" "$SANITY_STRICT"

  local passes=0 warns=0 fails=0
  local line method path status rest

  for line in "${CHECKS[@]}"; do
    local IFS=' '
    read -r method path status rest <<<"$line"
    # shellcheck disable=SC2086
    if run_check "$method" "$path" "$status" $rest; then
      if [[ "${CLASS:-pass}" == "warn" ]]; then
        warns=$((warns + 1))
      else
        passes=$((passes + 1))
      fi
    else
      fails=$((fails + 1))
    fi
  done

  # Run user API flow (if jq present)
  if run_user_flow; then
    passes=$((passes + 4))  # create, get, patch, deactivate
  else
    fails=$((fails + 1))
  fi

  printf '\nSummary: %d pass, %d warn, %d fail\n' "$passes" "$warns" "$fails"

  if (( fails > 0 )); then
    bad "Sanity checks failed"; exit 1
  fi
  if (( warns > 0 )); then
    warn "Sanity checks completed with warnings"; exit 0
  fi
  ok "All sanity checks passed"
}

main "$@"
