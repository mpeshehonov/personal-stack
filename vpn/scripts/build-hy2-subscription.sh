#!/usr/bin/env bash
# Build Happ subscription (sub.txt) from hysteria2 configs. Run on server after VPN changes.
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
HY2_DIR="$STACK_DIR/vpn/hysteria2"
SUB_FILE="$HY2_DIR/subscription/sub.txt"
ROUTING_LINK="http://89.124.70.216:8888/routing/happ-ru-direct.link"

export STACK_DIR
ROUTING_LINK="${ROUTING_LINK:-http://89.124.70.216:8888/routing/happ-ru-direct.link}"

python3 << PY
import os
import re
from pathlib import Path

hy2 = Path(os.environ["STACK_DIR"]) / "vpn/hysteria2"
sub_file = hy2 / "subscription" / "sub.txt"
routing_link = os.environ.get("ROUTING_LINK", "http://89.124.70.216:8888/routing/happ-ru-direct.link")
working = hy2 / "WORKING.txt"
pin = ""
if working.exists():
    m = re.search(r"pinSHA256=([A-Fa-f0-9]+)", working.read_text())
    if m:
        pin = m.group(1)

def load_cfg(port: int) -> tuple[str, str]:
    path = hy2 / f"config-{port}.yaml"
    if not path.exists():
        return "", ""
    text = path.read_text()
    pwd_m = re.search(r'password:\s*"([^"]+)"', text)
    obfs_m = re.search(r"salamander:\s*\n\s*password:\s*\"([^\"]+)\"", text)
    return (pwd_m.group(1) if pwd_m else "", obfs_m.group(1) if obfs_m else "")

lines = [
    "# Happ: re-import subscription after update",
    "include-all-networks-enable: true",
    "exclude-local-networks-enable: true",
    "exclude-apns-enable: true",
    "subscription-ping-onopen-enabled: true",
    f"routing-ru-direct: {routing_link}",
    "routing-ru-direct-json: http://89.124.70.216:8888/routing/happ-ru-direct.json",
    "",
]

host = "89.124.70.216"
sni = "yandex.ru"
pin_q = f"&pinSHA256={pin}" if pin else ""

for port, label, cfg in [
    (443, "Yandex-HY2-mobile", "mobile"),
    (36712, "Yandex-HY2", "36712"),
    (8443, "Yandex-HY2-8443", "8443"),
]:
    if cfg == "mobile":
        path = hy2 / "config-mobile.yaml"
        if not path.exists():
            continue
        text = path.read_text()
        pwd_m = re.search(r'password:\s*"([^"]+)"', text)
        obfs_m = re.search(r"salamander:\s*\n\s*password:\s*\"([^\"]+)\"", text)
        pwd = pwd_m.group(1) if pwd_m else ""
        obfs = obfs_m.group(1) if obfs_m else ""
    else:
        pwd, obfs = load_cfg(port)
    if not pwd:
        continue
    obfs_q = f"&obfs=salamander&obfs-password={obfs}" if obfs else ""
    uri = f"hysteria2://{pwd}@{host}:{port}/?sni={sni}{pin_q}{obfs_q}#{label}"
    lines.append(uri)

sub_file.parent.mkdir(parents=True, exist_ok=True)
sub_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {sub_file} ({len(lines)} lines)")
PY

echo "==> Reload subscription nginx"
cd "$HY2_DIR"
docker compose up -d hy2-subscription
