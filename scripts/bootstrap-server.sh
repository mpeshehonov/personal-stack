#!/usr/bin/env bash
# Run on fresh Ubuntu VPS as root: bash bootstrap-server.sh
set -euo pipefail

STACK_DIR="/opt/personal-stack"
AGENT_USER="agent"

echo "==> Updating system"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

echo "==> Installing base packages"
apt-get install -y -qq \
  ca-certificates curl git ufw fail2ban \
  python3 python3-pip python3-venv \
  rsync

echo "==> Installing Docker"
if ! command -v docker &>/dev/null; then
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

echo "==> Creating agent user"
if ! id "$AGENT_USER" &>/dev/null; then
  useradd -m -s /bin/bash "$AGENT_USER"
fi
usermod -aG docker "$AGENT_USER"

echo "==> UFW firewall"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Fail2ban SSH"
systemctl enable fail2ban
systemctl start fail2ban

echo "==> Stack directory"
mkdir -p "$STACK_DIR"/{secrets,agent/memory/daily,agent/memory/lessons,agent/tasks,scripts}
chown -R "$AGENT_USER:$AGENT_USER" "$STACK_DIR"
chmod 700 "$STACK_DIR/secrets"

echo "==> Python venv for agent services"
sudo -u "$AGENT_USER" python3 -m venv "$STACK_DIR/.venv"
sudo -u "$AGENT_USER" "$STACK_DIR/.venv/bin/pip" install -q --upgrade pip

echo "==> Bootstrap complete. Deploy code to $STACK_DIR and run deploy-stack.sh"
