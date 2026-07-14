#!/usr/bin/env bash
# Simulate a Cryptomus "paid" IPN for IB-16 E2E checkout testing.
# Requires secrets/.env.checkout with CHECKOUT_DELIVERY_SECRET + CRYPTOMUS_API_KEY.
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_FILE="${CHECKOUT_ENV:-$STACK_DIR/secrets/.env.checkout}"
BASE_URL="${CHECKOUT_BASE_URL:-https://mpeshekhonov.ru}"
PAYMENT_UUID="${1:-$(python3 -c 'import uuid; print(uuid.uuid4())')}"
PRICE_USD="${2:-19}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: missing $ENV_FILE — copy from secrets/.env.checkout.template" >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

if [[ -z "${CHECKOUT_DELIVERY_SECRET:-}" || -z "${CRYPTOMUS_API_KEY:-}" ]]; then
  echo "ERROR: CHECKOUT_DELIVERY_SECRET and CRYPTOMUS_API_KEY required in $ENV_FILE" >&2
  exit 1
fi

echo "Simulating Cryptomus IPN → $BASE_URL/api/checkout/ipn?provider=cryptomus (uuid=$PAYMENT_UUID, amount=\$$PRICE_USD)"

RESPONSE="$(python3 - "$BASE_URL" "$PAYMENT_UUID" "$PRICE_USD" <<'PY'
import hashlib
import json
import sys
import urllib.error
import urllib.request

base_url, payment_uuid, price_usd = sys.argv[1:4]
api_key = __import__("os").environ["CRYPTOMUS_API_KEY"]

amount = int(float(price_usd)) if float(price_usd) == int(float(price_usd)) else float(price_usd)
payload = {
    "uuid": payment_uuid,
    "order_id": f"sim-{payment_uuid}",
    "status": "paid",
    "amount": str(amount),
    "currency": "USDT",
}
encoded = __import__("base64").b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
sign = hashlib.md5((encoded + api_key).encode()).hexdigest()
body = {**payload, "sign": sign}

req = urllib.request.Request(
    f"{base_url.rstrip('/')}/api/checkout/ipn?provider=cryptomus",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
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

"$STACK_DIR/scripts/checkout-fix-perms.sh"
