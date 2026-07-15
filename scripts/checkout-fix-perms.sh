#!/usr/bin/env bash
# Fix bind-mount permissions for A4 checkout (site uid 1001 + host agent uid 1000).
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
CHECKOUT_DIR="$STACK_DIR/data/checkout"
ORDERS_FILE="$CHECKOUT_DIR/orders.json"
COMPOSE_FILE="$STACK_DIR/docker-compose.yml"
SITE_UID="${CHECKOUT_SITE_UID:-1001}"
HOST_UID="${CHECKOUT_HOST_UID:-$(id -u)}"
HOST_GID="${CHECKOUT_HOST_GID:-$(id -g)}"

mkdir -p "$CHECKOUT_DIR"
chmod 777 "$CHECKOUT_DIR" 2>/dev/null || true

_site_running() {
  docker compose -f "$COMPOSE_FILE" ps site --status running -q 2>/dev/null | grep -q .
}

# Shared rw: site container (nextjs) writes IPN orders; agent (host) runs checkout_sync.
if _site_running; then
  docker compose -f "$COMPOSE_FILE" exec -T -u root site sh -c '
    mkdir -p /app/data/checkout
    chmod 777 /app/data/checkout
    touch /app/data/checkout/orders.json
    chown '"$SITE_UID"':'"$HOST_GID"' /app/data/checkout/orders.json 2>/dev/null \
      || chown '"$SITE_UID"':65533 /app/data/checkout/orders.json 2>/dev/null \
      || true
    chmod 666 /app/data/checkout/orders.json
  ' 2>/dev/null || true
fi

if [[ -f "$ORDERS_FILE" ]]; then
  chmod 666 "$ORDERS_FILE" 2>/dev/null || true
  chown "$HOST_UID:$HOST_GID" "$ORDERS_FILE" 2>/dev/null || true
fi
