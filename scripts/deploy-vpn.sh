#!/usr/bin/env bash
# VPN deploy — Hy2 (UDP) + VLESS Reality (TCP) for whitelist / UDP-blocked carriers.
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> VPN sysctl tuning"
cp "$STACK_DIR/vpn/sysctl/99-vpn-tcp-tuning.conf" /etc/sysctl.d/
sysctl -p /etc/sysctl.d/99-vpn-tcp-tuning.conf

echo "==> UFW: Hy2 UDP + VLESS TCP + subscription"
ufw allow 36712/udp comment 'Hy2 primary' 2>/dev/null || ufw allow 36712/udp
ufw allow 8443/udp comment 'Hy2 backup' 2>/dev/null || ufw allow 8443/udp
ufw allow 2053/tcp comment 'VLESS Reality' 2>/dev/null || ufw allow 2053/tcp
ufw allow 8888/tcp comment 'Happ sub' 2>/dev/null || ufw allow 8888/tcp

echo "==> Stop legacy Hy2 listeners (keep 36712 + 8443)"
docker rm -f hysteria2-nl-443 hysteria2-nl-53 2>/dev/null || true

echo "==> Start Hysteria2 (36712 + 8443)"
cd "$STACK_DIR/vpn/hysteria2"
docker compose up -d --force-recreate hysteria2-36712 hysteria2-8443 hy2-subscription
sleep 2
bash verify-hy2.sh

echo "==> Start Xray VLESS Reality (TCP 2053, masquerade yandex.ru)"
cd "$STACK_DIR/vpn/xray-reality"
docker compose up -d --force-recreate
sleep 2
ss -tlnp | grep -E ':2053\b' && echo "Xray 2053 OK" || echo "WARN: 2053 not listening"

echo "==> Build Happ RU-direct routing profile"
bash "$STACK_DIR/vpn/scripts/build-happ-routing.sh"

echo "==> Build multi-protocol subscription"
export STACK_DIR
bash "$STACK_DIR/vpn/scripts/build-multi-subscription.sh"

echo "==> Caddy HTTPS on 443/TCP (site unchanged)"
cd "$STACK_DIR"
docker compose up -d caddy
sleep 2
curl -kfsS https://127.0.0.1/resume -o /dev/null -H "Host: mpeshekhonov.ru" && echo "HTTPS site OK"

echo ""
echo "==> Done. Import: http://89.124.70.216:8888/sub.txt"
echo "    Whitelist mode: pick VLESS Reality (TCP) first, then Hy2 if UDP works."
