"""Job hunt configuration from secrets/.env.jobhunt."""

from __future__ import annotations

import os

from orchestrator.config import load_env_file

load_env_file(".env.jobhunt")

JOBHUNT_ENABLED = os.environ.get("JOBHUNT_ENABLED", "false").lower() in ("true", "1", "yes")
JOBHUNT_HH_TEXT = os.environ.get("JOBHUNT_HH_TEXT", "frontend react typescript")
JOBHUNT_HH_QUERIES = os.environ.get("JOBHUNT_HH_QUERIES", "").strip()
JOBHUNT_MIN_MATCH = int(os.environ.get("JOBHUNT_MIN_MATCH", "55"))
JOBHUNT_MIN_SALARY_RUB = int(os.environ.get("JOBHUNT_MIN_SALARY_RUB", "250000"))
JOBHUNT_USER_AGENT = os.environ.get(
    "JOBHUNT_USER_AGENT",
    "personal-stack-agent/1.0 (kassady71@gmail.com)",
)
def hh_search_queries() -> list[str]:
    """Multiple HH queries for broader autopilot scan (deduped by vacancy id)."""
    if JOBHUNT_HH_QUERIES:
        parts = [q.strip() for q in JOBHUNT_HH_QUERIES.split(",") if q.strip()]
        if parts:
            return parts
    return [JOBHUNT_HH_TEXT]


JOBHUNT_HH_AREA = os.environ.get("JOBHUNT_HH_AREA", "113")
JOBHUNT_HH_PER_PAGE = int(os.environ.get("JOBHUNT_HH_PER_PAGE", "20"))
JOBHUNT_HH_MAX_PAGES = int(os.environ.get("JOBHUNT_HH_MAX_PAGES", "2"))
JOBHUNT_HH_ENABLED = os.environ.get("JOBHUNT_HH_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_HABR_ENABLED = os.environ.get("JOBHUNT_HABR_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_HABR_QUERY = os.environ.get("JOBHUNT_HABR_QUERY", "frontend react typescript")
