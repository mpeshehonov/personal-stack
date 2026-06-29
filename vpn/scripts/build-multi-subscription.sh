#!/usr/bin/env bash
# Build Happ subscription: Hy2 only (36712 Wi-Fi first, 8443 mobile backup).
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
HY2_DIR="$STACK_DIR/vpn/hysteria2"
SUB_FILE="$HY2_DIR/subscription/sub.txt"
SUB_PLAIN="$HY2_DIR/subscription/sub-plain.txt"
ROUTING_LINK="${ROUTING_LINK:-http://89.124.70.216:8888/routing/happ-ru-direct.link}"

export STACK_DIR ROUTING_LINK
python3 << 'PY'
import os
import re
from pathlib import Path
from urllib.parse import quote

stack = Path(os.environ["STACK_DIR"])
hy2_dir = stack / "vpn/hysteria2"
sub_file = hy2_dir / "subscription" / "sub.txt"
sub_plain = hy2_dir / "subscription" / "sub-plain.txt"
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


nodes: list[str] = []
for cfg, label in (
    ("config-36712.yaml", "Yandex-HY2-36712"),
    ("config-8443.yaml", "Yandex-HY2-8443"),
):
    uri = hy2_uri(cfg, label)
    if uri:
        nodes.append(uri)

if not nodes:
    raise SystemExit("No Hy2 nodes found in config-36712.yaml / config-8443.yaml")

common_headers = [
    "# Happ: delete old sub, import fresh. Wi-Fi: 36712. Mobile: 8443.",
    "include-all-networks-enable: true",
    "exclude-local-networks-enable: true",
    "exclude-apns-enable: true",
    "subscription-ping-onopen-enabled: false",
]

with_routing = common_headers + [
    f"routing-ru-direct: {routing_link}",
    "routing-ru-direct-json: http://89.124.70.216:8888/routing/happ-ru-direct.json",
    "",
] + nodes

plain = common_headers + [
    "# No routing — use if internet dead after connect (debug)",
    "",
] + nodes

sub_file.parent.mkdir(parents=True, exist_ok=True)
sub_file.write_text("\n".join(with_routing) + "\n", encoding="utf-8")
sub_plain.write_text("\n".join(plain) + "\n", encoding="utf-8")
print(f"Wrote {sub_file} and {sub_plain} ({len(nodes)} nodes)")
PY

echo "==> Reload subscription nginx"
cd "$HY2_DIR"
docker compose up -d hy2-subscription
