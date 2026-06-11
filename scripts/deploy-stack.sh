#!/usr/bin/env bash
# Run from repo root on server as agent user
set -euo pipefail

STACK_DIR="${STACK_DIR:-/opt/personal-stack}"
cd "$STACK_DIR"

echo "==> Installing Python dependencies"
.venv/bin/pip install -q -r agent/requirements.txt

echo "==> Building and starting Docker services"
docker compose build site
docker compose up -d

echo "==> Installing systemd units"
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo cp deploy/systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable agent-orchestrator telegram-bot personal-stack-daily.timer
sudo systemctl restart agent-orchestrator telegram-bot
sudo systemctl start personal-stack-daily.timer

echo "==> Deploy complete"
docker compose ps
systemctl status agent-orchestrator telegram-bot --no-pager || true
