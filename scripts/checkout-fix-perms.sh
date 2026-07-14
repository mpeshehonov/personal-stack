#!/usr/bin/env bash
# Fix bind-mount permissions for A4 checkout (site uid 1001 + host agent uid 1000).
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
CHECKOUT_DIR="$STACK_DIR/data/checkout"
ORDERS_FILE="$CHECKOUT_DIR/orders.json"
HOST_UID="${CHECKOUT_HOST_UID:-$(id -u)}"
HOST_GID="${CHECKOUT_HOST_GID:-$(id -g)}"

mkdir -p "$CHECKOUT_DIR"
chmod 777 "$CHECKOUT_DIR" 2>/dev/null || true

if [[ -f "$ORDERS_FILE" ]]; then
  if ! [[ -w "$ORDERS_FILE" ]]; then
    if docker compose -f "$STACK_DIR/docker-compose.yml" ps site --status running -q 2>/dev/null | grep -q .; then
      docker compose -f "$STACK_DIR/docker-compose.yml" exec -T -u root site \
        chown "$HOST_UID:$HOST_GID" /app/data/checkout/orders.json 2>/dev/null \
        || chmod 666 "$ORDERS_FILE" 2>/dev/null \
        || true
    fi
  fi
  chmod 664 "$ORDERS_FILE" 2>/dev/null || true
fi
