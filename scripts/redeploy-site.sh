#!/usr/bin/env bash
# Safe site redeploy — only path agents should use to restart the site
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> Rebuilding site container"
docker compose build site
docker compose up -d site caddy

echo "==> Reloading Caddy config"
docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile || docker compose restart caddy

echo "==> Health check"
sleep 3
curl -sf http://localhost/resume >/dev/null || curl -sf http://127.0.0.1:3000/resume >/dev/null || {
  echo "Site health check failed"
  exit 1
}
echo "Site OK"
