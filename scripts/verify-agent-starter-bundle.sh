#!/usr/bin/env bash
# Pre-flight check for Gumroad bundle: build, unpack, assert no secrets leak.
set -euo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
VERSION="${BUNDLE_VERSION:-0.3}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cd "$STACK_DIR"
OUT="$TMP/bundle.zip"
BUILD_LOG="$TMP/build.log"
"$STACK_DIR/scripts/bundle-agent-starter.sh" --version "$VERSION" --out "$OUT" >"$BUILD_LOG" 2>&1

# bundle-agent-starter may fall back to .tar.gz when zip is unavailable
if [[ -f "${OUT%.zip}.tar.gz" ]]; then
  OUT="${OUT%.zip}.tar.gz"
elif [[ ! -f "$OUT" ]]; then
  echo "ERROR: bundle not produced (see $BUILD_LOG)" >&2
  cat "$BUILD_LOG" >&2
  exit 1
fi

if [[ "$OUT" == *.tar.gz ]]; then
  tar -xzf "$OUT" -C "$TMP"
else
  unzip -q "$OUT" -d "$TMP"
fi

ROOT="$TMP/personal-stack-agent-starter"
[[ -d "$ROOT" ]] || { echo "ERROR: missing bundle root" >&2; exit 1; }

for required in BOOTSTRAP.md GUMROAD-LISTING.md VERSION.txt agent/orchestrator/main.py; do
  [[ -e "$ROOT/$required" ]] || { echo "ERROR: missing $required" >&2; exit 1; }
done

if find "$ROOT" -type f \( -path '*/secrets/.env' -o -name 'WORKING.txt' -o -name 'state.sqlite' \) 2>/dev/null | grep -q .; then
  echo "ERROR: sensitive file in bundle" >&2
  find "$ROOT" -type f \( -path '*/secrets/.env' -o -name 'WORKING.txt' -o -name 'state.sqlite' \) >&2
  exit 1
fi

if grep -rqE 'shpss_[a-zA-Z0-9]{16,}|shpat_[a-zA-Z0-9]{16,}' "$ROOT" 2>/dev/null; then
  echo "ERROR: possible live Shopify token in bundle" >&2
  grep -rnE 'shpss_[a-zA-Z0-9]{16,}|shpat_[a-zA-Z0-9]{16,}' "$ROOT" >&2 | head -5
  exit 1
fi

echo "OK: bundle v${VERSION} pre-flight passed ($(stat -c '%s' "$OUT" 2>/dev/null || stat -f '%z' "$OUT") bytes)"
