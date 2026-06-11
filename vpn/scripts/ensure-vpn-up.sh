#!/usr/bin/env bash
# Wrapper for idempotent VPN container ensure (see ../ensure-up.sh).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../ensure-up.sh" "$@"
