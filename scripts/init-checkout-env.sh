#!/usr/bin/env bash
# IB-16: bootstrap secrets/.env.checkout from template (safe, idempotent).
# Generates CHECKOUT_DELIVERY_SECRET if missing; never overwrites provider API keys.
# Usage:
#   ./scripts/init-checkout-env.sh              # delivery secret only
#   ./scripts/init-checkout-env.sh --sandbox-ipn  # + sandbox NOWPAYMENTS_IPN_SECRET for E2E
set -euo pipefail

SANDBOX_IPN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sandbox-ipn) SANDBOX_IPN=1; shift ;;
    -h|--help)
      echo "Usage: $0 [--sandbox-ipn]"
      echo "  --sandbox-ipn  generate sandbox NOWPAYMENTS_IPN_SECRET when no provider set (E2E only)"
      exit 0
      ;;
    *) echo "Unknown option: $1 (try --help)" >&2; exit 1 ;;
  esac
done

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
TEMPLATE="$STACK_DIR/secrets/.env.checkout.template"
ENV_FILE="${CHECKOUT_ENV:-$STACK_DIR/secrets/.env.checkout}"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "ERROR: missing $TEMPLATE" >&2
  exit 1
fi

created=0
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$TEMPLATE" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "OK: created $ENV_FILE from template"
  created=1
else
  echo "OK: $ENV_FILE already exists (not overwritten)"
fi

# Inject delivery secret only when empty / placeholder
delivery_line="$(grep -E '^CHECKOUT_DELIVERY_SECRET=' "$ENV_FILE" || true)"
delivery_val="${delivery_line#CHECKOUT_DELIVERY_SECRET=}"
if [[ -z "$delivery_val" ]]; then
  secret="$(openssl rand -hex 32)"
  if grep -q '^CHECKOUT_DELIVERY_SECRET=' "$ENV_FILE"; then
    sed -i "s/^CHECKOUT_DELIVERY_SECRET=.*/CHECKOUT_DELIVERY_SECRET=$secret/" "$ENV_FILE"
  else
    echo "CHECKOUT_DELIVERY_SECRET=$secret" >>"$ENV_FILE"
  fi
  echo "OK: generated CHECKOUT_DELIVERY_SECRET"
else
  echo "OK: CHECKOUT_DELIVERY_SECRET already set"
fi

has_nowpayments=0
has_cryptomus=0
grep -qE '^NOWPAYMENTS_IPN_SECRET=.+$' "$ENV_FILE" && has_nowpayments=1 || true
grep -qE '^CRYPTOMUS_API_KEY=.+$' "$ENV_FILE" && has_cryptomus=1 || true

if [[ "$SANDBOX_IPN" -eq 1 && "$has_nowpayments" -eq 0 && "$has_cryptomus" -eq 0 ]]; then
  sandbox_secret="sandbox-$(openssl rand -hex 24)"
  if grep -q '^NOWPAYMENTS_IPN_SECRET=' "$ENV_FILE"; then
    sed -i "s/^NOWPAYMENTS_IPN_SECRET=.*/NOWPAYMENTS_IPN_SECRET=$sandbox_secret/" "$ENV_FILE"
  else
    echo "NOWPAYMENTS_IPN_SECRET=$sandbox_secret" >>"$ENV_FILE"
  fi
  has_nowpayments=1
  echo "OK: generated sandbox NOWPAYMENTS_IPN_SECRET (E2E only — replace before live sales)"
fi

echo ""
echo "== IB-16 checkout bootstrap =="
echo "File: $ENV_FILE"
echo ""

if [[ "$has_nowpayments" -eq 0 && "$has_cryptomus" -eq 0 ]]; then
  echo "NEXT: fill at least one provider in $ENV_FILE:"
  echo "  • NOWPayments: NOWPAYMENTS_IPN_SECRET (+ optional NOWPAYMENTS_API_KEY)"
  echo "  • Cryptomus:   CRYPTOMUS_API_KEY + CRYPTOMUS_MERCHANT_ID"
  echo ""
fi

echo "Then:"
echo "  1. ./scripts/redeploy-site.sh"
echo "  2. ./scripts/checkout-status.sh              # gap report (no secrets printed)"
echo "  3. ./scripts/verify-checkout-readiness.sh   # expect configured:true"
echo "  4. ./scripts/run-checkout-e2e.sh            # sandbox IPN → delivery → checkout_sync"
echo ""
echo "Docs: agent/memory/products/checkout-setup.md"

if [[ "$created" -eq 1 ]]; then
  exit 0
fi
