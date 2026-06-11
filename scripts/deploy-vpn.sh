#!/usr/bin/env bash
# VPN-only deploy — recreates VPN containers. Do NOT run from site deploy.
# Site deploy uses scripts/deploy-from-git.sh (site + caddy only) + vpn/ensure-up.sh.
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> VPN sysctl tuning"
cp "$STACK_DIR/vpn/sysctl/99-vpn-tcp-tuning.conf" /etc/sysctl.d/
sysctl -p /etc/sysctl.d/99-vpn-tcp-tuning.conf

echo "==> UFW: Hy2 UDP + subscription"
ufw allow 36712/udp
ufw allow 8443/udp
ufw allow 8888/tcp

echo "==> Stop Xray on 443 (keep 2053 TCP fallback only)"
cd "$STACK_DIR/vpn/xray-reality"
docker compose up -d --force-recreate

echo "==> Start Hysteria2 (primary VPN)"
cd "$STACK_DIR/vpn/hysteria2"
docker compose up -d --force-recreate
sleep 3
bash verify-hy2.sh

echo "==> Caddy HTTPS on 443/TCP (site)"
cd "$STACK_DIR"
docker compose up -d --force-recreate caddy
sleep 2
curl -kfsS https://127.0.0.1/resume -o /dev/null && echo "HTTPS site OK"

echo "==> Links: vpn/hysteria2/WORKING.txt"
