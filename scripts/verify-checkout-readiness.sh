#!/usr/bin/env bash
# Pre-flight for IB-16 crypto checkout — no provider keys required.
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
BASE_URL="${CHECKOUT_BASE_URL:-https://mpeshekhonov.ru}"
FAIL=0

warn() { echo "WARN: $*" >&2; }
fail() { echo "ERROR: $*" >&2; FAIL=1; }
ok() { echo "OK: $*"; }

cd "$STACK_DIR"

# --- local artifacts ---
[[ -f "$STACK_DIR/secrets/.env.checkout.template" ]] \
  || fail "missing secrets/.env.checkout.template"

if [[ -f "$STACK_DIR/secrets/.env.checkout" ]]; then
  ok "secrets/.env.checkout present"
else
  warn "secrets/.env.checkout missing (checkout will return configured:false)"
fi

BUNDLE_FOUND=0
for f in \
  "$STACK_DIR/dist/personal-stack-agent-starter-v0.3.tar.gz" \
  "$STACK_DIR/dist/personal-stack-agent-starter-v0.3.zip"; do
  if [[ -f "$f" ]]; then
    ok "bundle artifact $(basename "$f") ($(stat -c '%s' "$f" 2>/dev/null || stat -f '%z' "$f") bytes)"
    BUNDLE_FOUND=1
    break
  fi
done
[[ "$BUNDLE_FOUND" -eq 1 ]] || fail "no bundle in dist/ (run bundle-agent-starter.sh)"

[[ -d "$STACK_DIR/data/checkout" ]] \
  || fail "missing data/checkout directory"

# --- agent sync ---
SYNC_OUT="$(cd "$STACK_DIR/agent" && PYTHONPATH=. python3 -m finance.checkout_sync --dry-run 2>&1)" \
  || { fail "checkout_sync --dry-run failed"; SYNC_OUT=""; }
if [[ -n "$SYNC_OUT" ]]; then
  echo "$SYNC_OUT" | grep -q '"dry_run": true' \
    && ok "checkout_sync --dry-run" \
    || fail "checkout_sync unexpected output"
fi

# --- prod endpoint (after deploy) ---
IPN_BODY="$(curl -sf "${BASE_URL}/api/checkout/ipn" 2>/dev/null || true)"
if [[ -z "$IPN_BODY" ]]; then
  fail "GET ${BASE_URL}/api/checkout/ipn unreachable"
elif echo "$IPN_BODY" | grep -q '"service"[[:space:]]*:[[:space:]]*"a4-checkout-ipn"'; then
  ok "IPN health endpoint returns JSON"
  if echo "$IPN_BODY" | grep -q '"configured"[[:space:]]*:[[:space:]]*true'; then
    ok "checkout configured (secrets loaded)"
  else
    warn "checkout not configured yet — fill secrets/.env.checkout and redeploy"
  fi
else
  fail "IPN endpoint does not return a4-checkout JSON (route missing or stale deploy?)"
fi

# --- optional bundle deep check ---
if [[ "${SKIP_BUNDLE_VERIFY:-}" != "1" ]]; then
  "$STACK_DIR/scripts/verify-agent-starter-bundle.sh" || fail "bundle pre-flight failed"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "CHECKOUT READINESS: FAILED" >&2
  exit 1
fi

echo "CHECKOUT READINESS: PASSED"
