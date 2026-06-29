#!/usr/bin/env bash
# VPN deploy — Hysteria2 only (UDP 8443 + 36712).
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> VPN sysctl tuning"
cp "$STACK_DIR/vpn/sysctl/99-vpn-tcp-tuning.conf" /etc/sysctl.d/
sysctl -p /etc/sysctl.d/99-vpn-tcp-tuning.conf

echo "==> UFW: Hy2 UDP + subscription"
ufw allow 36712/udp comment 'Hy2 backup' 2>/dev/null || ufw allow 36712/udp
ufw allow 8443/udp comment 'Hy2 primary mobile' 2>/dev/null || ufw allow 8443/udp
ufw allow 8888/tcp comment 'Happ sub' 2>/dev/null || ufw allow 8888/tcp

echo "==> Stop legacy / unused VPN (VLESS, old Hy2 ports)"
docker rm -f xray-reality-vless hysteria2-nl-443 hysteria2-nl-53 2>/dev/null || true

echo "==> Start Hysteria2 (8443 + 36712)"
cd "$STACK_DIR/vpn/hysteria2"
docker compose up -d hysteria2-8443 hysteria2-36712 hy2-subscription
sleep 2
bash verify-hy2.sh

echo "==> Build Happ RU-direct routing profile"
bash "$STACK_DIR/vpn/scripts/build-happ-routing.sh"

echo "==> Build Hy2 subscription"
export STACK_DIR
bash "$STACK_DIR/vpn/scripts/build-multi-subscription.sh"

echo "==> Caddy HTTPS on 443/TCP (site unchanged)"
cd "$STACK_DIR"
docker compose up -d caddy
sleep 2
curl -kfsS https://127.0.0.1/resume -o /dev/null -H "Host: mpeshekhonov.ru" && echo "HTTPS site OK"

echo ""
echo "==> Done. Import: http://89.124.70.216:8888/sub.txt"
echo "    Mobile: Yandex-HY2-8443 first. Wi-Fi: try 36712 if needed."
