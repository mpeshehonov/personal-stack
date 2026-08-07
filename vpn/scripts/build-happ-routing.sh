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

# One-tap import page (open on phone → Happ)
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Import RU-direct → Happ</title>
<meta http-equiv="refresh" content="0;url={link}"/>
</head>
<body style="font-family:system-ui;padding:1.5rem;max-width:40rem">
<h1>RU-direct</h1>
<p>Если Happ не открылся сам — нажми кнопку:</p>
<p><a href="{link}" style="font-size:1.2rem">Открыть в Happ</a></p>
<p style="color:#666;font-size:.9rem">Или скопируй содержимое
<a href="happ-ru-direct.link">happ-ru-direct.link</a>
(строка <code>happ://routing/onadd/…</code>) и вставь через Import profile.</p>
</body>
</html>
"""
(sub_dir / "import.html").write_text(html, encoding="utf-8")
(routing / "import.html").write_text(html, encoding="utf-8")

# Round-trip check
decoded = json.loads(base64.b64decode(b64))
assert decoded["Name"] == profile["Name"]
assert decoded["LastUpdated"] == profile["LastUpdated"]
# Keep payload small — huge headers get dropped by some clients
if len(link) > 3500:
    raise SystemExit(f"Routing deeplink too long ({len(link)} chars) — trim DirectSites")

print(f"DirectSites: {len(direct)} rules ({len(extra)} extra domains)")
print(f"LastUpdated: {profile['LastUpdated']}")
print(f"Deeplink: {len(link)} chars")
print(f"Wrote {out_json}")
print(f"Wrote {out_link}")
print(f"Wrote {sub_dir / 'import.html'}")
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
