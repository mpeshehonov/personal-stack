#!/usr/bin/env bash
# VPN-only deploy — recreates VPN containers. Do NOT run from site deploy.
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> VPN sysctl tuning"
cp "$STACK_DIR/vpn/sysctl/99-vpn-tcp-tuning.conf" /etc/sysctl.d/
sysctl -p /etc/sysctl.d/99-vpn-tcp-tuning.conf

echo "==> UFW: Hy2 UDP + subscription"
ufw allow 443/udp
ufw allow 36712/udp
ufw allow 8443/udp
ufw allow 8888/tcp

echo "==> Stop legacy Xray (removed)"
docker rm -f xray-reality-vless 2>/dev/null || true

echo "==> Start Hysteria2 (primary VPN — 443/8443/36712 UDP)"
cd "$STACK_DIR/vpn/hysteria2"
# Bootstrap config-443 from template if missing (copy creds from 8443)
if [[ ! -f config-443.yaml ]] && [[ -f config-8443.yaml ]]; then
  cp config-8443.yaml config-443.yaml
  sed -i 's/:8443/:443/' config-443.yaml 2>/dev/null || sed -i '' 's/:8443/:443/' config-443.yaml
fi
docker compose up -d --force-recreate
sleep 3
bash verify-hy2.sh

echo "==> Build Happ RU-direct routing profile"
bash "$STACK_DIR/vpn/scripts/build-happ-routing.sh"

echo "==> Build Hy2 subscription (no VLESS)"
export STACK_DIR
bash "$STACK_DIR/vpn/scripts/build-hy2-subscription.sh"

echo "==> Caddy HTTPS on 443/TCP (site)"
cd "$STACK_DIR"
docker compose up -d --force-recreate caddy
sleep 2
curl -kfsS https://127.0.0.1/resume -o /dev/null && echo "HTTPS site OK"

echo "==> Links: vpn/hysteria2/WORKING.txt + http://89.124.70.216:8888/sub.txt"
