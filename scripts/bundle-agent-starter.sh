#!/usr/bin/env bash
# Build a Gumroad-ready zip of Personal Stack Agent Starter (no secrets, no runtime state).
# Usage:
#   ./scripts/bundle-agent-starter.sh
#   ./scripts/bundle-agent-starter.sh --out /tmp/personal-stack-agent-starter.zip
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
VERSION="${BUNDLE_VERSION:-0.3}"
OUT="${OUT:-$STACK_DIR/dist/personal-stack-agent-starter-v${VERSION}.zip}"
FORMAT="zip"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--out PATH] [--version VER] [--format zip|tgz]"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ "$OUT" == *.tgz || "$OUT" == *.tar.gz ]]; then
  FORMAT="tgz"
elif [[ "$OUT" == *.zip ]]; then
  FORMAT="zip"
fi

cd "$STACK_DIR"
mkdir -p "$(dirname "$OUT")"

STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

ROOT="$STAGING/personal-stack-agent-starter"
mkdir -p "$ROOT"

echo "==> Staging bundle v${VERSION} -> $OUT"

# Core tree: preserve top-level layout (agent/, site/, scripts/, docs/).
rsync -a \
  --exclude='.git/' \
  --exclude='secrets/' \
  --exclude='state.sqlite' \
  --exclude='bounty/research_cache/' \
  --exclude='*.sqlite' \
  --exclude='*.sqlite-journal' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.venv/' \
  --exclude='venv/' \
  agent/ "$ROOT/agent/"

rsync -a \
  --exclude='node_modules/' \
  --exclude='.next/' \
  --exclude='public/resume.pdf' \
  site/ "$ROOT/site/"

rsync -a scripts/ "$ROOT/scripts/"
rsync -a docs/ "$ROOT/docs/"
cp README.md "$ROOT/README.md"

# Buyer-facing docs at bundle root.
cp agent/memory/products/delivery-readme.md "$ROOT/BOOTSTRAP.md"
cp agent/memory/products/agent-starter.md "$ROOT/GUMROAD-LISTING.md"

# Placeholder secrets layout (templates only).
mkdir -p "$ROOT/secrets"
if [[ -f secrets/.env.example ]]; then
  cp secrets/.env.example "$ROOT/secrets/.env.example"
fi
for f in secrets/*.template; do
  [[ -f "$f" ]] && cp "$f" "$ROOT/secrets/"
done
chmod 700 "$ROOT/secrets"
find "$ROOT/secrets" -type f -exec chmod 600 {} \;

cat > "$ROOT/VERSION.txt" <<EOF
personal-stack-agent-starter
version: ${VERSION}
built: $(date -u +%Y-%m-%dT%H:%M:%SZ)
source: bundle-agent-starter.sh
EOF

# Sanity: no real secrets or VPN live configs in the archive.
if find "$ROOT" -type f \( -path '*/secrets/.env' -o -name 'WORKING.txt' -o -name 'config.json' \) 2>/dev/null | grep -q .; then
  echo "ERROR: sensitive file leaked into staging" >&2
  find "$ROOT" -type f \( -path '*/secrets/.env' -o -name 'WORKING.txt' \) >&2
  exit 1
fi

rm -f "$OUT"
if [[ "$FORMAT" == "zip" ]] && command -v zip >/dev/null 2>&1; then
  (
    cd "$STAGING"
    zip -rq "$OUT" personal-stack-agent-starter
  )
elif [[ "$FORMAT" == "tgz" ]] || [[ "$FORMAT" == "zip" ]]; then
  OUT="${OUT%.zip}.tar.gz"
  (
    cd "$STAGING"
    tar -czf "$OUT" personal-stack-agent-starter
  )
  echo "==> Note: zip unavailable; produced tar.gz instead"
else
  echo "ERROR: unsupported format $FORMAT" >&2
  exit 1
fi

BYTES=$(stat -c '%s' "$OUT" 2>/dev/null || stat -f '%z' "$OUT")
echo "==> Done: $OUT ($BYTES bytes)"
echo "Upload to Gumroad as file delivery, or attach BOOTSTRAP.md in product description."
