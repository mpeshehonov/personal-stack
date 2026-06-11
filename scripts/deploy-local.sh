#!/usr/bin/env bash
# Local helper: push to GitHub, then trigger server deploy.
# Usage:
#   ./scripts/deploy-local.sh              # push + remote deploy
#   SKIP_PUSH=1 ./scripts/deploy-local.sh  # remote deploy only
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEPLOY_REMOTE="${DEPLOY_REMOTE:-agent@89.124.70.216}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
STACK_DIR="${STACK_DIR:-/opt/personal-stack}"

if [[ "${SKIP_PUSH:-0}" != "1" ]]; then
  if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Not a git repository. Run: git init && git remote add origin git@github.com:YOU/personal-stack.git"
    exit 1
  fi

  echo "==> Pushing origin/$DEPLOY_BRANCH"
  git push origin "$DEPLOY_BRANCH"
fi

echo "==> Deploying on $DEPLOY_REMOTE"
ssh "$DEPLOY_REMOTE" "cd $STACK_DIR && ./scripts/deploy-from-git.sh"
