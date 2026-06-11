#!/usr/bin/env bash
# Server-side deploy: pull latest code, rebuild site, restart services.
# Run on the server as the agent user:
#   cd /opt/personal-stack && ./scripts/deploy-from-git.sh
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
AGENT_USER="${AGENT_USER:-agent}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
GIT_BRANCH="${GIT_BRANCH:-main}"
RELOAD_CADDY="${RELOAD_CADDY:-1}"
RESTART_SYSTEMD="${RESTART_SYSTEMD:-1}"

cd "$STACK_DIR"

if [[ "$(id -un)" != "$AGENT_USER" ]]; then
  echo "Run as $AGENT_USER (current: $(id -un))"
  exit 1
fi

fix_permissions() {
  local owner
  owner="$(stat -c '%U' "$STACK_DIR" 2>/dev/null || echo "$AGENT_USER")"

  if [[ "$owner" != "$AGENT_USER" ]]; then
    echo "==> Fixing stack ownership ($owner -> $AGENT_USER)"
    sudo chown -R "$AGENT_USER:$AGENT_USER" "$STACK_DIR"
  fi

  # Git metadata can end up root-owned after manual fixes; normalize without touching secrets mode.
  if [[ -d "$STACK_DIR/.git" ]] && [[ "$(stat -c '%U' "$STACK_DIR/.git")" != "$AGENT_USER" ]]; then
    sudo chown -R "$AGENT_USER:$AGENT_USER" "$STACK_DIR/.git"
  fi

  if [[ -d "$STACK_DIR/secrets" ]]; then
    chmod 700 "$STACK_DIR/secrets"
    find "$STACK_DIR/secrets" -type f -exec chmod 600 {} \;
  fi

  chmod +x "$STACK_DIR"/scripts/*.sh 2>/dev/null || true
}

echo "==> Pulling $GIT_REMOTE/$GIT_BRANCH"
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Not a git repository. See docs/DEPLOY.md for bootstrap."
  exit 1
fi

git fetch "$GIT_REMOTE"
git checkout "$GIT_BRANCH"
git pull --ff-only "$GIT_REMOTE" "$GIT_BRANCH"

fix_permissions

echo "==> Installing Python dependencies"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r agent/requirements.txt

echo "==> Building and starting Docker services"
docker compose build site
docker compose up -d

if [[ "$RESTART_SYSTEMD" == "1" ]]; then
  echo "==> Restarting systemd services"
  sudo systemctl restart agent-orchestrator telegram-bot
fi

if [[ "$RELOAD_CADDY" == "1" ]]; then
  echo "==> Reloading Caddy"
  docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile \
    || docker compose restart caddy
fi

echo "==> Health check"
sleep 3
curl -sf http://localhost/resume >/dev/null \
  || curl -sf http://127.0.0.1:3000/resume >/dev/null \
  || { echo "Site health check failed"; exit 1; }

echo "==> Deploy complete"
docker compose ps
systemctl status agent-orchestrator telegram-bot --no-pager || true
