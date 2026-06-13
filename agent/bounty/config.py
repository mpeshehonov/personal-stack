"""Bug bounty semi-auto configuration."""

from __future__ import annotations

import os

from orchestrator.config import load_env_file

load_env_file(".env.bounty")

BOUNTY_ENABLED = os.environ.get("BOUNTY_ENABLED", "true").lower() in ("1", "true", "yes")
BOUNTY_AUTO_SUBMIT = os.environ.get("BOUNTY_AUTO_SUBMIT", "true").lower() in ("1", "true", "yes")
BOUNTY_MAX_PENDING = int(os.environ.get("BOUNTY_MAX_PENDING", "2"))
BOUNTY_RESEARCH_COOLDOWN_HOURS = int(os.environ.get("BOUNTY_RESEARCH_COOLDOWN_HOURS", "20"))

HACKERONE_API_USERNAME = os.environ.get("HACKERONE_API_USERNAME", "").strip()
HACKERONE_API_TOKEN = os.environ.get("HACKERONE_API_TOKEN", "").strip()

KV_PROGRAM_INDEX = "bounty_program_index"
KV_LAST_RESEARCH = "bounty_last_research_ts"
