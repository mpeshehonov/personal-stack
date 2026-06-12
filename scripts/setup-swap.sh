#!/usr/bin/env bash
# One-time: add swap as OOM safety net on small VPS (run as root).
set -euo pipefail

SWAP_SIZE="${SWAP_SIZE:-2G}"
SWAP_FILE="${SWAP_FILE:-/swapfile}"
SWAPPINESS="${SWAPPINESS:-10}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root"
  exit 1
fi

if swapon --show | grep -q "$SWAP_FILE"; then
  echo "Swap already active: $SWAP_FILE"
  swapon --show
  exit 0
fi

if [[ ! -f "$SWAP_FILE" ]]; then
  echo "==> Creating $SWAP_FILE ($SWAP_SIZE)"
  fallocate -l "$SWAP_SIZE" "$SWAP_FILE" || dd if=/dev/zero of="$SWAP_FILE" bs=1M count=2048 status=progress
  chmod 600 "$SWAP_FILE"
  mkswap "$SWAP_FILE"
fi

echo "==> Enabling swap"
swapon "$SWAP_FILE"

grep -q "$SWAP_FILE" /etc/fstab || echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab

sysctl -w vm.swappiness="$SWAPPINESS"
grep -q '^vm.swappiness' /etc/sysctl.conf \
  && sed -i "s/^vm.swappiness.*/vm.swappiness=$SWAPPINESS/" /etc/sysctl.conf \
  || echo "vm.swappiness=$SWAPPINESS" >> /etc/sysctl.conf

echo "==> Done"
free -h
swapon --show
