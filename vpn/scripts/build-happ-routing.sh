#!/usr/bin/env bash
# Build Happ routing profile: RU sites bypass VPN, rest via proxy.
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
SKIP_RELOAD=0
for arg in "$@"; do
  case "$arg" in
    --skip-reload) SKIP_RELOAD=1 ;;
  esac
done

export STACK_DIR
python3 <<'PY'
import base64
import json
import os
import time
from pathlib import Path

stack = Path(os.environ.get("STACK_DIR", "/opt/personal-stack"))
routing = stack / "vpn/routing"
sites_file = routing / "ru-direct-sites.txt"
base_json = routing / "happ-ru-direct.base.json"
out_json = routing / "happ-ru-direct.json"
out_link = routing / "happ-ru-direct.link"
sub_dir = stack / "vpn/hysteria2/subscription/routing"

extra: list[str] = []
for line in sites_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    extra.append(
        f"domain:{line}"
        if not line.startswith(("domain:", "geosite:", "full:", "regexp:"))
        else line
    )

profile = json.loads(base_json.read_text(encoding="utf-8"))
direct = list(profile.get("DirectSites", []))
seen = set(direct)
for item in extra:
    if item not in seen:
        direct.append(item)
        seen.add(item)
profile["DirectSites"] = direct
# Bump so Happ "Update routing" actually replaces an existing profile
profile["LastUpdated"] = str(int(time.time()))

# Compact JSON → standard base64 (with padding). Happ is picky about malformed b64.
payload = json.dumps(profile, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
b64 = base64.b64encode(payload).decode("ascii")
assert len(b64) % 4 == 0, f"bad base64 length {len(b64)}"
link = f"happ://routing/onadd/{b64}"

out_json.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_link.write_text(link + "\n", encoding="utf-8")

sub_dir.mkdir(parents=True, exist_ok=True)
(sub_dir / "happ-ru-direct.json").write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
(sub_dir / "happ-ru-direct.link").write_text(out_link.read_text(encoding="utf-8"), encoding="utf-8")

# Round-trip check
decoded = json.loads(base64.b64decode(b64))
assert decoded["Name"] == profile["Name"]
assert decoded["LastUpdated"] == profile["LastUpdated"]

print(f"DirectSites: {len(direct)} rules ({len(extra)} extra domains)")
print(f"LastUpdated: {profile['LastUpdated']}")
print(f"Wrote {out_json}")
print(f"Wrote {out_link} ({len(b64)} b64 chars)")
PY

if [[ "$SKIP_RELOAD" == "1" ]]; then
  echo "==> Skip nginx reload (--skip-reload)"
  exit 0
fi

echo "==> Reload subscription nginx (pick up new routing files)"
cd "$STACK_DIR/vpn/hysteria2"
docker compose up -d hy2-subscription --force-recreate
sleep 1

echo "==> Verify routing URLs"
curl -fsSI "http://127.0.0.1:8888/routing/happ-ru-direct.json" | head -1
curl -fsSI "http://127.0.0.1:8888/routing/happ-ru-direct.link" | head -1
echo "Routing profile OK"
