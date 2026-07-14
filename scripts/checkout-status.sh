#!/usr/bin/env bash
# IB-16: human-readable checkout pipeline status (no secret values printed).
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_FILE="${CHECKOUT_ENV:-$STACK_DIR/secrets/.env.checkout}"
BASE_URL="${CHECKOUT_BASE_URL:-https://mpeshekhonov.ru}"

pass=0
warn=0
fail=0

mark_pass() { echo "  [OK]   $*"; pass=$((pass + 1)); }
mark_warn() { echo "  [WARN] $*"; warn=$((warn + 1)); }
mark_fail() { echo "  [FAIL] $*"; fail=$((fail + 1)); }

echo "== IB-16 A4 checkout status =="
echo ""

# --- secrets ---
echo "Secrets:"
if [[ -f "$STACK_DIR/secrets/.env.checkout.template" ]]; then
  mark_pass "template present"
else
  mark_fail "missing secrets/.env.checkout.template"
fi

if [[ -f "$ENV_FILE" ]]; then
  mark_pass "secrets/.env.checkout present"
else
  mark_fail "secrets/.env.checkout missing — run ./scripts/init-checkout-env.sh"
fi

has_delivery=0
has_nowpayments=0
has_cryptomus=0
has_sandbox=0
if [[ -f "$ENV_FILE" ]]; then
  grep -qE '^CHECKOUT_DELIVERY_SECRET=.+$' "$ENV_FILE" && has_delivery=1 || true
  grep -qE '^NOWPAYMENTS_IPN_SECRET=.+$' "$ENV_FILE" && has_nowpayments=1 || true
  grep -qE '^CRYPTOMUS_API_KEY=.+$' "$ENV_FILE" && has_cryptomus=1 || true
  grep -qE '^NOWPAYMENTS_IPN_SECRET=sandbox-' "$ENV_FILE" && has_sandbox=1 || true
fi

if [[ "$has_delivery" -eq 1 ]]; then
  mark_pass "CHECKOUT_DELIVERY_SECRET set"
else
  mark_fail "CHECKOUT_DELIVERY_SECRET empty — run init-checkout-env.sh"
fi

if [[ "$has_nowpayments" -eq 1 ]]; then
  if [[ "$has_sandbox" -eq 1 ]]; then
    mark_warn "NOWPAYMENTS_IPN_SECRET is sandbox (E2E only — replace before live sales)"
  else
    mark_pass "NOWPAYMENTS_IPN_SECRET set"
  fi
elif [[ "$has_cryptomus" -eq 1 ]]; then
  mark_pass "Cryptomus credentials set"
else
  mark_fail "no payment provider — fill NOWPAYMENTS_IPN_SECRET or CRYPTOMUS_* (or init --sandbox-ipn)"
fi

echo ""
echo "Artifacts:"
bundle_ok=0
for f in \
  "$STACK_DIR/dist/personal-stack-agent-starter-v0.3.tar.gz" \
  "$STACK_DIR/dist/personal-stack-agent-starter-v0.3.zip"; do
  if [[ -f "$f" ]]; then
    mark_pass "bundle $(basename "$f")"
    bundle_ok=1
    break
  fi
done
[[ "$bundle_ok" -eq 1 ]] || mark_fail "no bundle in dist/ — run bundle-agent-starter.sh"

[[ -d "$STACK_DIR/data/checkout" ]] \
  && mark_pass "data/checkout directory" \
  || mark_fail "missing data/checkout"

echo ""
echo "Production:"
IPN_BODY="$(curl -sf "${BASE_URL}/api/checkout/ipn" 2>/dev/null || true)"
if [[ -z "$IPN_BODY" ]]; then
  mark_fail "GET ${BASE_URL}/api/checkout/ipn unreachable"
elif echo "$IPN_BODY" | grep -q '"service"[[:space:]]*:[[:space:]]*"a4-checkout-ipn"'; then
  mark_pass "IPN health endpoint live"
  if echo "$IPN_BODY" | grep -q '"configured"[[:space:]]*:[[:space:]]*true'; then
    mark_pass "checkout configured (secrets loaded in container)"
  else
    mark_warn "configured:false — redeploy after filling secrets/.env.checkout"
  fi
else
  mark_fail "IPN endpoint unexpected response"
fi

ORDERS_PATH="$STACK_DIR/data/checkout/orders.json"
if [[ -f "$ORDERS_PATH" ]]; then
  FULFILLED="$(python3 - "$ORDERS_PATH" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
print(sum(1 for o in data.get("orders", []) if o.get("status") == "fulfilled"))
PY
)"
  if [[ "$FULFILLED" -gt 0 ]]; then
    mark_pass "$FULFILLED fulfilled order(s) in orders.json"
  else
    mark_warn "no fulfilled orders yet — run run-checkout-e2e.sh after configured:true"
  fi
else
  mark_warn "orders.json not created yet (first IPN will create it)"
fi

echo ""
echo "Next steps:"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "  1. ./scripts/init-checkout-env.sh --sandbox-ipn   # or fill real provider keys"
elif [[ "$has_delivery" -eq 0 || ( "$has_nowpayments" -eq 0 && "$has_cryptomus" -eq 0 ) ]]; then
  echo "  1. ./scripts/init-checkout-env.sh --sandbox-ipn   # E2E without provider account"
  echo "     or edit secrets/.env.checkout with real NOWPayments/Cryptomus keys"
else
  echo "  1. ./scripts/redeploy-site.sh                     # if configured:false"
  echo "  2. ./scripts/run-checkout-e2e.sh                  # sandbox IPN → delivery → sync"
  echo "  3. cd agent && PYTHONPATH=. python3 -m finance.checkout_sync"
fi
echo ""
echo "Summary: $pass OK, $warn WARN, $fail FAIL"
[[ "$fail" -eq 0 ]]
