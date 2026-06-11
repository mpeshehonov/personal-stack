"""Git commit, push, and deploy after agent task runs."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from orchestrator.config import STACK_DIR

logger = logging.getLogger(__name__)

DEPLOY_SCRIPT = STACK_DIR / "scripts" / "deploy-from-git.sh"


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd or STACK_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )


def git_status_porcelain() -> str:
    r = _run(["git", "status", "--porcelain"])
    return r.stdout.strip()


def has_uncommitted_changes() -> bool:
    return bool(git_status_porcelain())


def pull_latest() -> tuple[bool, str]:
    """Fetch and fast-forward to origin/main. Fails if working tree is dirty."""
    dirty = git_status_porcelain()
    if dirty:
        lines = dirty.splitlines()[:8]
        return False, "Локальные изменения без commit:\n" + "\n".join(lines)

    r = _run(["git", "fetch", "origin"])
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "git fetch failed").strip()

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch_name = branch.stdout.strip() or "main"
    r = _run(["git", "pull", "--ff-only", "origin", branch_name])
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "git pull failed").strip()
    return True, (r.stdout or "Already up to date.").strip()


def commit_and_push(message: str) -> tuple[bool, str]:
    """Stage all changes, commit, push. Returns (success, log)."""
    if not has_uncommitted_changes():
        return True, "Нет незакоммиченных изменений."

    lines: list[str] = []
    for cmd in (
        ["git", "add", "-A"],
        ["git", "commit", "-m", message],
        ["git", "push", "origin", "HEAD"],
    ):
        r = _run(cmd)
        if r.stdout.strip():
            lines.append(r.stdout.strip())
        if r.stderr.strip():
            lines.append(r.stderr.strip())
        if r.returncode != 0:
            if cmd[1] == "commit" and "nothing to commit" in (r.stdout + r.stderr).lower():
                return True, "Коммит не нужен (nothing to commit)."
            return False, "\n".join(lines) or f"Команда failed: {' '.join(cmd)}"

    return True, "\n".join(lines) or "Коммит и push выполнены."


def bot_files_changed() -> bool:
    status = git_status_porcelain()
    for line in status.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        path = parts[-1]
        if path.startswith("agent/telegram_bot/"):
            return True
    r = _run(["git", "diff", "--name-only", "HEAD~1", "HEAD"])
    if r.returncode == 0:
        return any(n.startswith("agent/telegram_bot/") for n in r.stdout.splitlines())
    return False


def deploy(*, restart_telegram: bool = True, restart_orchestrator: bool = True) -> tuple[bool, str]:
    if not DEPLOY_SCRIPT.is_file():
        return False, f"Нет скрипта: {DEPLOY_SCRIPT}"

    env = os.environ.copy()
    env["RESTART_TELEGRAM"] = "1" if restart_telegram else "0"
    env["RESTART_ORCHESTRATOR"] = "1" if restart_orchestrator else "0"

    r = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT)],
        cwd=STACK_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        logger.warning("deploy failed: %s", out[-2000:])
        return False, out[-1500:] or "deploy-from-git.sh завершился с ошибкой"
    return True, out[-800:] or "Deploy OK"


def apply_task_deploy(task_summary: str) -> str:
    """Commit, push, deploy after a /task agent run. Returns Russian status text."""
    parts: list[str] = []

    if has_uncommitted_changes():
        msg = task_summary.split("\n", 1)[0].strip()[:72] or "agent task"
        if not msg.lower().startswith(("feat", "fix", "chore", "docs")):
            msg = f"feat: {msg}"
        ok, log = commit_and_push(msg)
        parts.append("Коммит: OK" if ok else f"Коммит: ошибка\n{log[:400]}")
        if not ok:
            return "\n".join(parts)
    else:
        parts.append("Коммит: изменений нет")

    bot_changed = bot_files_changed()
    ok, log = deploy(
        restart_telegram=False,
        restart_orchestrator=True,
    )
    parts.append("Deploy: OK" if ok else f"Deploy: ошибка\n{log[:500]}")

    if bot_changed and ok:
        r = _run(["sudo", "systemctl", "restart", "telegram-bot"])
        parts.append(
            "Telegram-бот перезапущен (обновлён код бота)."
            if r.returncode == 0
            else "Не удалось перезапустить telegram-bot (нужен sudo)."
        )

    return "\n".join(parts)
