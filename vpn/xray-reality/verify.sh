#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

echo "[1] Xray config test..."
docker run --rm -v "$PWD/config.json:/etc/xray/config.json:ro" \
  --entrypoint /usr/bin/xray teddysun/xray:latest -test -config /etc/xray/config.json

echo "[2] Server container..."
docker ps --filter name=xray-reality-vless --format '{{.Names}} {{.Status}}' | grep -q Up || {
  docker compose up -d
  sleep 2
}

echo "[3] E2E via VLESS Reality (public IP)..."
docker rm -f xray-verify-client 2>/dev/null || true
docker run -d --name xray-verify-client --network host \
  -v "$PWD/test-client.json:/etc/xray/config.json:ro" \
  --entrypoint /usr/bin/xray teddysun/xray:latest run -c /etc/xray/config.json
sleep 2
IP=$(curl -sS --max-time 20 --socks5-hostname 127.0.0.1:10888 https://api.ipify.org || true)
docker rm -f xray-verify-client 2>/dev/null || true

if [ "$IP" = "89.124.70.216" ]; then
  echo "OK: proxy egress IP = $IP"
  exit 0
fi

echo "FAIL: expected 89.124.70.216, got: ${IP:-timeout}"
exit 1
