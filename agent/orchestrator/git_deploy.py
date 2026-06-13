"""Git commit, push, and deploy after agent task runs."""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.config import STACK_DIR

logger = logging.getLogger(__name__)

DEPLOY_SCRIPT = STACK_DIR / "scripts" / "deploy-from-git.sh"
GIT_USER_NAME = os.environ.get("GIT_AUTHOR_NAME", "Maksim Peshekhonov")
GIT_USER_EMAIL = os.environ.get("GIT_AUTHOR_EMAIL", "kassady71@gmail.com")


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd or STACK_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )


def ensure_git_identity() -> None:
    """Set repo-local git author if missing (server agent commits)."""
    for key, value in (("user.name", GIT_USER_NAME), ("user.email", GIT_USER_EMAIL)):
        r = _run(["git", "config", "--get", key])
        if r.returncode != 0 or not r.stdout.strip():
            _run(["git", "config", key, value])


def git_status_porcelain() -> str:
    r = _run(["git", "status", "--porcelain"])
    return r.stdout.strip()


def has_uncommitted_changes() -> bool:
    return bool(git_status_porcelain())


MEMORY_PATH_PREFIXES = ("agent/memory/",)


def _dirty_paths() -> list[str]:
    status = git_status_porcelain()
    if not status:
        return []
    paths: list[str] = []
    for line in status.splitlines():
        parts = line.strip().split()
        if parts:
            paths.append(parts[-1].rstrip("/"))
    return paths


def _is_memory_only_dirty() -> bool:
    paths = _dirty_paths()
    if not paths:
        return False
    return all(
        any(p == prefix.rstrip("/") or p.startswith(prefix) for prefix in MEMORY_PATH_PREFIXES)
        for p in paths
    )


def clean_junk_untracked() -> list[str]:
    """Remove accidental shell redirect files like '=22.6' from repo root."""
    removed: list[str] = []
    for path in STACK_DIR.glob("=*"):
        if path.is_file():
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def pull_latest() -> tuple[bool, str]:
    """Fetch and fast-forward to origin/main. Fails if working tree is dirty."""
    removed = clean_junk_untracked()
    if has_uncommitted_changes() and _is_memory_only_dirty():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        ok, log = commit_and_push(f"chore(memory): daily artifacts {today}")
        if not ok:
            return False, f"Не удалось закоммитить memory перед pull:\n{log[:400]}"

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
    extra = f" (удалён мусор: {', '.join(removed)})" if removed else ""
    return True, (r.stdout or "Already up to date.").strip() + extra


def commit_and_push(message: str) -> tuple[bool, str]:
    """Stage all changes, commit, push. Returns (success, log)."""
    ensure_git_identity()
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


def apply_daily_commit(summary: str = "") -> str:
    """Commit and push daily agent memory writes. No deploy."""
    if not has_uncommitted_changes():
        return "Коммит daily: изменений нет"

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = f"chore(memory): daily log {today}"
    if summary.strip():
        hint = summary.strip().split("\n", 1)[0][:60]
        if hint and not hint.startswith("#"):
            msg = f"chore(memory): daily log {today} — {hint}"

    ok, log = commit_and_push(msg)
    if ok:
        return "Коммит daily: OK"
    return f"Коммит daily: ошибка\n{log[:500]}"


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
