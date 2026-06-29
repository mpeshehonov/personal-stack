#!/usr/bin/env bash
# Build Happ subscription: Hy2 (36712, 8443) + VLESS Reality (TCP) for whitelist / UDP-blocked networks.
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
HY2_DIR="$STACK_DIR/vpn/hysteria2"
XRAY_DIR="$STACK_DIR/vpn/xray-reality"
SUB_FILE="$HY2_DIR/subscription/sub.txt"
ROUTING_LINK="${ROUTING_LINK:-http://89.124.70.216:8888/routing/happ-ru-direct.link}"

export STACK_DIR ROUTING_LINK
python3 << 'PY'
import os
import re
from pathlib import Path
from urllib.parse import quote

stack = Path(os.environ["STACK_DIR"])
hy2_dir = stack / "vpn/hysteria2"
xray_dir = stack / "vpn/xray-reality"
sub_file = hy2_dir / "subscription" / "sub.txt"
routing_link = os.environ.get("ROUTING_LINK", "http://89.124.70.216:8888/routing/happ-ru-direct.link")
host = "89.124.70.216"
sni = "yandex.ru"


def hy2_uri(config_name: str, label: str) -> str:
    path = hy2_dir / config_name
    if not path.exists():
        return ""
    text = path.read_text()
    pwd_m = re.search(r'password:\s*"([^"]+)"', text)
    obfs_m = re.search(r'salamander:\s*\n\s*password:\s*"([^"]+)"', text)
    port_m = re.search(r"listen:\s*:(\d+)", text)
    if not pwd_m or not port_m:
        return ""
    pwd = quote(pwd_m.group(1), safe="")
    port = port_m.group(1)
    obfs = obfs_m.group(1) if obfs_m else ""
    pin = ""
    working = hy2_dir / "WORKING.txt"
    if working.exists():
        m = re.search(r"pinSHA256=([A-Fa-f0-9]+)", working.read_text())
        if m:
            pin = m.group(1)
    pin_q = f"&pinSHA256={pin}" if pin else ""
    obfs_q = f"&obfs=salamander&obfs-password={quote(obfs, safe='')}" if obfs else ""
    return f"hysteria2://{pwd}@{host}:{port}/?sni={sni}{pin_q}{obfs_q}#{quote(label)}"


def vless_uris_from_working() -> list[str]:
    working = xray_dir / "WORKING.txt"
    if not working.exists():
        return []
    uris: list[str] = []
    for line in working.read_text().splitlines():
        line = line.strip()
        if line.startswith("vless://"):
            uris.append(line)
    return uris


lines = [
    "# Happ: re-import after deploy — whitelist mode: try VLESS Reality (TCP) first",
    "include-all-networks-enable: true",
    "exclude-local-networks-enable: true",
    "exclude-apns-enable: true",
    "subscription-ping-onopen-enabled: true",
    f"routing-ru-direct: {routing_link}",
    "routing-ru-direct-json: http://89.124.70.216:8888/routing/happ-ru-direct.json",
    "",
]

# TCP first — best when mobile carrier blocks UDP / non-whitelist
for vless in vless_uris_from_working():
    lines.append(vless)

lines.append("")
# Hy2 backup ports
for cfg, label in (
    ("config-36712.yaml", "Yandex-HY2-36712"),
    ("config-8443.yaml", "Yandex-HY2-8443"),
):
    uri = hy2_uri(cfg, label)
    if uri:
        lines.append(uri)

sub_file.parent.mkdir(parents=True, exist_ok=True)
sub_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {sub_file} ({len(lines)} lines, vless={len(vless_uris_from_working())})")
PY

echo "==> Reload subscription nginx"
cd "$HY2_DIR"
docker compose up -d hy2-subscription
