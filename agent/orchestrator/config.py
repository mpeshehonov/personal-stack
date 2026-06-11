"""Shared configuration and paths."""

from __future__ import annotations

import os
from pathlib import Path

STACK_DIR = Path(os.environ.get("STACK_DIR", "/opt/personal-stack"))
AGENT_DIR = STACK_DIR / "agent"
SECRETS_DIR = STACK_DIR / "secrets"
MEMORY_DIR = AGENT_DIR / "memory"
TASKS_DIR = AGENT_DIR / "tasks"
STATE_DB = AGENT_DIR / "state.sqlite"
SITE_DIR = STACK_DIR / "site"
SITE_URL = os.environ.get("SITE_URL", "https://mpeshekhonov.ru")
PUBLIC_SITE_URL = os.environ.get("PUBLIC_SITE_URL", SITE_URL)
SITE_LOCAL_HOST = os.environ.get("SITE_LOCAL_HOST", "mpeshekhonov.ru")


def load_env_file(name: str) -> None:
    path = SECRETS_DIR / name
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())
