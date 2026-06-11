#!/usr/bin/env bash
# Safe Docker cleanup — never removes running containers or VPN images.
set -euo pipefail

KEEP_BUILD_CACHE_H="${DOCKER_PRUNE_BUILD_CACHE_H:-168}"   # 7 days
RESERVED_SPACE="${DOCKER_PRUNE_RESERVED_SPACE:-2GB}"

echo "==> Docker disk before prune"
docker system df 2>/dev/null || true

echo "==> Capping build cache (reserved-space ${RESERVED_SPACE})"
docker builder prune -f --reserved-space "${RESERVED_SPACE}" 2>/dev/null || true

echo "==> Pruning build cache older than ${KEEP_BUILD_CACHE_H}h"
docker builder prune -f --filter "until=${KEEP_BUILD_CACHE_H}h" 2>/dev/null || true

echo "==> Pruning dangling images only"
docker image prune -f 2>/dev/null || true

echo "==> Docker disk after prune"
docker system df 2>/dev/null || true
