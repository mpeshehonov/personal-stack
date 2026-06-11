#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

docker rm -f hy2-verify-client 2>/dev/null || true
docker run -d --name hy2-verify-client --network host \
  -v "$PWD/client-test.yaml:/etc/hysteria/client.yaml:ro" \
  tobyxdd/hysteria:latest client -c /etc/hysteria/client.yaml
sleep 4
IP=$(curl -sS --max-time 25 --socks5-hostname 127.0.0.1:10889 https://api.ipify.org || true)
docker rm -f hy2-verify-client 2>/dev/null || true
if [ "$IP" = "89.124.70.216" ]; then
  echo "OK: $IP"
  exit 0
fi
echo "FAIL: got ${IP:-timeout}"
exit 1
