#!/usr/bin/env bash
# Idempotent: ensure VPN containers are running. Never force-recreate.
# Safe to call after site deploy — does not restart healthy containers.
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"

VPN_CONTAINERS=(
  hysteria2-nl-36712
  hysteria2-nl-8443
  hy2-subscription
  xray-reality-vless
)

container_running() {
  local name="$1"
  [[ "$(docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null || echo false)" == "true" ]]
}

missing=()
for name in "${VPN_CONTAINERS[@]}"; do
  if ! container_running "$name"; then
    missing+=("$name")
  fi
done

if ((${#missing[@]} == 0)); then
  echo "VPN OK: all containers running"
  for name in "${VPN_CONTAINERS[@]}"; do
    started="$(docker inspect -f '{{.State.StartedAt}}' "$name")"
    echo "  $name  started=$started"
  done
  exit 0
fi

echo "VPN down: ${missing[*]} — starting stacks (no recreate)"
cd "$STACK_DIR/vpn/xray-reality"
docker compose up -d
cd "$STACK_DIR/vpn/hysteria2"
docker compose up -d

sleep 2
still_missing=()
for name in "${VPN_CONTAINERS[@]}"; do
  if ! container_running "$name"; then
    still_missing+=("$name")
  fi
done

if ((${#still_missing[@]} > 0)); then
  echo "VPN ensure-up failed: ${still_missing[*]} still not running" >&2
  docker ps -a --filter "name=hysteria2" --filter "name=xray" --filter "name=hy2" \
    --format 'table {{.Names}}\t{{.Status}}' >&2
  exit 1
fi

echo "VPN recovered"
for name in "${VPN_CONTAINERS[@]}"; do
  started="$(docker inspect -f '{{.State.StartedAt}}' "$name")"
  echo "  $name  started=$started"
done
