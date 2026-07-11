#!/usr/bin/env bash
# Simulate a NOWPayments "finished" IPN for IB-16 E2E checkout testing.
# Requires secrets/.env.checkout with CHECKOUT_DELIVERY_SECRET + NOWPAYMENTS_IPN_SECRET.
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_FILE="${CHECKOUT_ENV:-$STACK_DIR/secrets/.env.checkout}"
BASE_URL="${CHECKOUT_BASE_URL:-https://mpeshekhonov.ru}"
PAYMENT_ID="${1:-test-$(date +%s)}"
PRICE_USD="${2:-19}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: missing $ENV_FILE — copy from secrets/.env.checkout.template" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

if [[ -z "${CHECKOUT_DELIVERY_SECRET:-}" || -z "${NOWPAYMENTS_IPN_SECRET:-}" ]]; then
  echo "ERROR: CHECKOUT_DELIVERY_SECRET and NOWPAYMENTS_IPN_SECRET required in $ENV_FILE" >&2
  exit 1
fi

echo "Simulating NOWPayments IPN → $BASE_URL/api/checkout/ipn (payment_id=$PAYMENT_ID, price=\$$PRICE_USD)"

RESPONSE="$(python3 - "$BASE_URL" "$PAYMENT_ID" "$PRICE_USD" <<'PY'
import hashlib
import hmac
import json
import sys
import urllib.error
import urllib.request

base_url, payment_id, price_usd = sys.argv[1:4]
secret = __import__("os").environ["NOWPAYMENTS_IPN_SECRET"]

def sort_keys(v):
    if isinstance(v, dict):
        return {k: sort_keys(v[k]) for k in sorted(v)}
    if isinstance(v, list):
        return [sort_keys(x) for x in v]
    return v

body = {
    "payment_id": payment_id,
    "payment_status": "finished",
    "price_amount": int(float(price_usd)) if float(price_usd) == int(float(price_usd)) else float(price_usd),
    "pay_amount": int(float(price_usd)) if float(price_usd) == int(float(price_usd)) else float(price_usd),
    "pay_currency": "usdt",
    "order_id": f"sim-{payment_id}",
}
payload = json.dumps(sort_keys(body), separators=(",", ":"))
sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha512).hexdigest()

req = urllib.request.Request(
    f"{base_url.rstrip('/')}/api/checkout/ipn",
    data=payload.encode(),
    headers={
        "Content-Type": "application/json",
        "x-nowpayments-sig": sig,
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode(), file=sys.stderr)
    sys.exit(e.code)
PY
)"

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

DELIVERY_URL="$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('delivery_url',''))" 2>/dev/null || true)"

if [[ -n "$DELIVERY_URL" ]]; then
  echo ""
  echo "Delivery URL: $DELIVERY_URL"
  HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' "$DELIVERY_URL")"
  echo "GET delivery → HTTP $HTTP_CODE (expect 200 with bundle)"
  echo ""
  echo "Next: cd agent && PYTHONPATH=. python3 -m finance.checkout_sync"
else
  echo "WARN: no delivery_url in response — check configured secrets and redeploy" >&2
  exit 1
fi
