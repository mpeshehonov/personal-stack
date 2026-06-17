"""Bug bounty semi-auto configuration."""

from __future__ import annotations

import os

from orchestrator.config import load_env_file

load_env_file(".env.bounty")

BOUNTY_ENABLED = os.environ.get("BOUNTY_ENABLED", "true").lower() in ("1", "true", "yes")
BOUNTY_AUTO_SUBMIT = os.environ.get("BOUNTY_AUTO_SUBMIT", "true").lower() in ("1", "true", "yes")
BOUNTY_MAX_PENDING = int(os.environ.get("BOUNTY_MAX_PENDING", "2"))
BOUNTY_RESEARCH_COOLDOWN_HOURS = int(os.environ.get("BOUNTY_RESEARCH_COOLDOWN_HOURS", "20"))
BOUNTY_PROGRAMS_PER_CYCLE = int(os.environ.get("BOUNTY_PROGRAMS_PER_CYCLE", "3"))
BOUNTY_REVIEW_ENABLED = os.environ.get("BOUNTY_REVIEW_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_MIN_QUALITY_SCORE = int(os.environ.get("BOUNTY_MIN_QUALITY_SCORE", "85"))
BOUNTY_RESEARCH_PHASES = os.environ.get("BOUNTY_RESEARCH_PHASES", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_SAVE_LEADS = os.environ.get("BOUNTY_SAVE_LEADS", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_SHOPIFY_FOCUS = os.environ.get("BOUNTY_SHOPIFY_FOCUS", "true").lower() in (
    "1",
    "true",
    "yes",
)

HACKERONE_API_USERNAME = os.environ.get("HACKERONE_API_USERNAME", "").strip()
# Some accounts use a separate token identifier from HackerOne settings (Basic auth username).
HACKERONE_API_IDENTIFIER = (
    os.environ.get("HACKERONE_API_IDENTIFIER", "").strip() or HACKERONE_API_USERNAME
)
HACKERONE_API_TOKEN = os.environ.get("HACKERONE_API_TOKEN", "").strip()

KV_PROGRAM_INDEX = "bounty_program_index"
KV_LAST_RESEARCH = "bounty_last_research_ts"
