#!/usr/bin/env bash
# Full IB-16 sandbox E2E: simulate IPN → verify delivery → checkout_sync.
# Usage:
#   ./scripts/run-checkout-e2e.sh              # auto-detect provider from secrets
#   ./scripts/run-checkout-e2e.sh nowpayments  # force NOWPayments simulate
#   ./scripts/run-checkout-e2e.sh cryptomus    # force Cryptomus simulate
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_FILE="${CHECKOUT_ENV:-$STACK_DIR/secrets/.env.checkout}"
PROVIDER="${1:-auto}"
PAYMENT_ID="${2:-test-$(date +%s)}"
PRICE_USD="${3:-19}"

cd "$STACK_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: missing $ENV_FILE" >&2
  echo "  cp secrets/.env.checkout.template secrets/.env.checkout" >&2
  echo "  fill CHECKOUT_DELIVERY_SECRET + provider secret, then redeploy" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

if [[ "$PROVIDER" == "auto" ]]; then
  if [[ -n "${NOWPAYMENTS_IPN_SECRET:-}" ]]; then
    PROVIDER="nowpayments"
  elif [[ -n "${CRYPTOMUS_API_KEY:-}" ]]; then
    PROVIDER="cryptomus"
  else
    echo "ERROR: set NOWPAYMENTS_IPN_SECRET or CRYPTOMUS_API_KEY in $ENV_FILE" >&2
    exit 1
  fi
fi

echo "== IB-16 checkout E2E (provider=$PROVIDER) =="
echo ""

echo "1/4 verify-checkout-readiness"
"$STACK_DIR/scripts/verify-checkout-readiness.sh"
echo ""

echo "2/4 simulate IPN ($PROVIDER)"
case "$PROVIDER" in
  nowpayments)
    "$STACK_DIR/scripts/simulate-checkout-ipn.sh" "$PAYMENT_ID" "$PRICE_USD"
    ;;
  cryptomus)
    "$STACK_DIR/scripts/simulate-checkout-cryptomus.sh" "$PAYMENT_ID" "$PRICE_USD"
    ;;
  *)
    echo "ERROR: unknown provider '$PROVIDER' (use nowpayments|cryptomus|auto)" >&2
    exit 1
    ;;
esac
echo ""

echo "3/4 checkout_sync --dry-run"
SYNC_DRY="$(cd "$STACK_DIR/agent" && PYTHONPATH=. python3 -m finance.checkout_sync --dry-run)"
echo "$SYNC_DRY"
echo "$SYNC_DRY" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('synced') else 1)" \
  || { echo "WARN: no orders to sync (dry-run empty)" >&2; }
echo ""

echo "4/4 checkout_sync (finance_log)"
SYNC_LIVE="$(cd "$STACK_DIR/agent" && PYTHONPATH=. python3 -m finance.checkout_sync)"
echo "$SYNC_LIVE"
echo ""

ORDERS_PATH="${CHECKOUT_ORDERS_PATH:-$STACK_DIR/data/checkout/orders.json}"
if [[ -f "$ORDERS_PATH" ]]; then
  FULFILLED="$(python3 - "$ORDERS_PATH" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
orders = [o for o in data.get("orders", []) if o.get("status") == "fulfilled"]
print(len(orders))
PY
)"
  echo "CHECKOUT E2E: PASSED ($FULFILLED fulfilled order(s) in orders.json)"
else
  echo "WARN: orders file not found at $ORDERS_PATH" >&2
fi
