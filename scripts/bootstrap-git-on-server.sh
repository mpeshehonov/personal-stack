#!/usr/bin/env bash
# One-time server bootstrap: attach GitHub remote while preserving secrets and runtime state.
# Run on the server as agent:
#   GITHUB_REPO=git@github.com:YOU/personal-stack.git ./scripts/bootstrap-git-on-server.sh
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
AGENT_USER="${AGENT_USER:-agent}"
GITHUB_REPO="${GITHUB_REPO:-}"
GIT_BRANCH="${GIT_BRANCH:-main}"

if [[ -z "$GITHUB_REPO" ]]; then
  echo "Set GITHUB_REPO, e.g. git@github.com:you/personal-stack.git"
  exit 1
fi

if [[ "$(id -un)" != "$AGENT_USER" ]]; then
  echo "Run as $AGENT_USER"
  exit 1
fi

BACKUP="$(mktemp -d /tmp/personal-stack-bootstrap.XXXXXX)"
cleanup() { rm -rf "$BACKUP"; }
trap cleanup EXIT

echo "==> Backing up server-only paths"
[[ -d "$STACK_DIR/secrets" ]] && cp -a "$STACK_DIR/secrets" "$BACKUP/"
[[ -d "$STACK_DIR/.venv" ]] && cp -a "$STACK_DIR/.venv" "$BACKUP/"
[[ -f "$STACK_DIR/agent/state.sqlite" ]] && cp -a "$STACK_DIR/agent/state.sqlite" "$BACKUP/"
[[ -d "$STACK_DIR/vpn/hysteria2/certs" ]] && cp -a "$STACK_DIR/vpn/hysteria2/certs" "$BACKUP/hy2-certs"
if [[ -d "$STACK_DIR/vpn" ]]; then
  mkdir -p "$BACKUP/vpn"
  for path in \
    hysteria2/config-36712.yaml \
    hysteria2/config-8443.yaml \
    hysteria2/client-test.yaml \
    hysteria2/WORKING.txt \
    hysteria2/subscription \
    xray-reality/config.json \
    xray-reality/test-client.json \
    xray-reality/WORKING.txt; do
    [[ -e "$STACK_DIR/vpn/$path" ]] && mkdir -p "$BACKUP/vpn/$(dirname "$path")" && cp -a "$STACK_DIR/vpn/$path" "$BACKUP/vpn/$path"
  done
fi

if [[ -d "$STACK_DIR/.git" ]] && git -C "$STACK_DIR" rev-parse --is-inside-work-tree &>/dev/null; then
  echo "==> Attaching remote to existing checkout"
  cd "$STACK_DIR"
  git remote remove origin 2>/dev/null || true
  git remote add origin "$GITHUB_REPO"
  git fetch origin
  git checkout -B "$GIT_BRANCH" "origin/$GIT_BRANCH" 2>/dev/null \
    || git reset --hard "origin/$GIT_BRANCH"
else
  echo "==> Cloning into $STACK_DIR"
  rm -rf "$STACK_DIR"
  git clone --branch "$GIT_BRANCH" "$GITHUB_REPO" "$STACK_DIR"
  cd "$STACK_DIR"
fi

echo "==> Restoring server-only paths"
[[ -d "$BACKUP/secrets" ]] && cp -a "$BACKUP/secrets" "$STACK_DIR/"
[[ -d "$BACKUP/.venv" ]] && cp -a "$BACKUP/.venv" "$STACK_DIR/"
[[ -f "$BACKUP/state.sqlite" ]] && cp -a "$BACKUP/state.sqlite" "$STACK_DIR/agent/"
[[ -d "$BACKUP/hy2-certs" ]] && mkdir -p "$STACK_DIR/vpn/hysteria2/certs" \
  && cp -a "$BACKUP/hy2-certs/." "$STACK_DIR/vpn/hysteria2/certs/"
if [[ -d "$BACKUP/vpn" ]]; then
  cp -a "$BACKUP/vpn/." "$STACK_DIR/vpn/"
fi

chmod 700 "$STACK_DIR/secrets" 2>/dev/null || true
find "$STACK_DIR/secrets" -type f -exec chmod 600 {} \; 2>/dev/null || true
chmod +x "$STACK_DIR"/scripts/*.sh

echo "==> Bootstrap complete. Run ./scripts/deploy-from-git.sh for full deploy."
