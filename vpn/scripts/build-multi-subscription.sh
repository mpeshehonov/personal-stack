#!/usr/bin/env bash
# Build Happ subscription: Hy2 nodes + RU-direct routing in the body.
# Happ applies `happ://routing/onadd/...` on subscription update (no separate import).
set -euo pipefail
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
HY2_DIR="$STACK_DIR/vpn/hysteria2"
SUB_DIR="$HY2_DIR/subscription"
SUB_FILE="$SUB_DIR/sub.txt"
SUB_PLAIN="$SUB_DIR/sub-plain.txt"
ROUTING_LINK_FILE="${ROUTING_LINK_FILE:-$STACK_DIR/vpn/routing/happ-ru-direct.link}"

# Refresh routing profile + happ:// deeplink first (no nginx bounce yet)
bash "$STACK_DIR/vpn/scripts/build-happ-routing.sh" --skip-reload

export STACK_DIR ROUTING_LINK_FILE SUB_FILE SUB_PLAIN
python3 << 'PY'
import os
import re
from pathlib import Path
from urllib.parse import quote

stack = Path(os.environ["STACK_DIR"])
hy2_dir = stack / "vpn/hysteria2"
sub_file = Path(os.environ["SUB_FILE"])
sub_plain = Path(os.environ["SUB_PLAIN"])
link_file = Path(os.environ["ROUTING_LINK_FILE"])
host = "89.124.70.216"
sni = "yandex.ru"

if not link_file.exists():
    raise SystemExit(f"Missing routing link: {link_file} (run build-happ-routing.sh)")
routing_deeplink = link_file.read_text(encoding="utf-8").strip()
if not routing_deeplink.startswith("happ://routing/"):
    raise SystemExit(f"Bad routing deeplink in {link_file}")


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
    if not pin:
        raise SystemExit(
            f"Missing pinSHA256 in {hy2_dir / 'WORKING.txt'} — Happ 4.8+ requires pinnedPeerCertSha256"
        )
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
    "# Happ: update sub → RU-direct routing auto-applies (onadd).",
    "include-all-networks-enable: true",
    "exclude-local-networks-enable: true",
    "exclude-apns-enable: true",
    "subscription-ping-onopen-enabled: false",
]

# Official Happ: put happ://routing/onadd/... in the subscription body.
with_routing = common_headers + [
    routing_deeplink,
    "",
] + nodes

plain = [
    "# Happ debug: nodes only, no routing",
    "include-all-networks-enable: true",
    "exclude-local-networks-enable: true",
    "exclude-apns-enable: true",
    "subscription-ping-onopen-enabled: false",
    "",
] + nodes

sub_file.parent.mkdir(parents=True, exist_ok=True)
sub_file.write_text("\n".join(with_routing) + "\n", encoding="utf-8")
sub_plain.write_text("\n".join(plain) + "\n", encoding="utf-8")
print(f"Wrote {sub_file} ({len(nodes)} nodes + routing onadd, {len(routing_deeplink)} chars deeplink)")
print(f"Wrote {sub_plain} (no routing)")
PY

echo "==> Reload subscription nginx"
cd "$HY2_DIR"
docker compose up -d hy2-subscription --force-recreate
sleep 1

echo "==> Verify"
curl -fsS "http://127.0.0.1:8888/sub.txt" | head -8
echo "..."
curl -fsS "http://127.0.0.1:8888/sub.txt" | grep -c '^happ://routing/onadd/' || true
curl -fsSI "http://127.0.0.1:8888/routing/happ-ru-direct.link" | head -1
