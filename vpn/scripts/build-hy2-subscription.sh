#!/usr/bin/env bash
# Build Happ subscription (sub.txt) — Hy2 nodes on 8443 + 36712.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/build-multi-subscription.sh"
