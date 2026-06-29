#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

verify_port() {
  local port="$1"
  local name="hy2-verify-${port}"
  docker rm -f "$name" 2>/dev/null || true
  sed "s/127.0.0.1:36712/127.0.0.1:${port}/" client-test.yaml > "/tmp/hy2-client-${port}.yaml"
  docker run -d --name "$name" --network host \
    -v "/tmp/hy2-client-${port}.yaml:/etc/hysteria/client.yaml:ro" \
    tobyxdd/hysteria:latest client -c /etc/hysteria/client.yaml
  sleep 4
  local ip
  ip=$(curl -sS --max-time 25 --socks5-hostname 127.0.0.1:10889 https://api.ipify.org || true)
  docker rm -f "$name" 2>/dev/null || true
  if [ "$ip" = "89.124.70.216" ]; then
    echo "OK ${port}: $ip"
    return 0
  fi
  echo "FAIL ${port}: got ${ip:-timeout}"
  return 1
}

failed=0
for port in 8443 36712; do
  verify_port "$port" || failed=1
done
exit "$failed"
