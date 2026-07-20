"""Job hunt configuration from secrets/.env.jobhunt."""

from __future__ import annotations

import os

from orchestrator.config import load_env_file

load_env_file(".env.jobhunt")

JOBHUNT_ENABLED = os.environ.get("JOBHUNT_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_HH_TEXT = os.environ.get(
    "JOBHUNT_HH_TEXT",
    "senior frontend react typescript",
)
JOBHUNT_HH_QUERIES = os.environ.get(
    "JOBHUNT_HH_QUERIES",
    "senior frontend react typescript,senior product engineer react,next.js frontend remote,lead frontend react",
).strip()
JOBHUNT_MIN_MATCH = int(os.environ.get("JOBHUNT_MIN_MATCH", "70"))
JOBHUNT_MIN_SALARY_RUB = int(os.environ.get("JOBHUNT_MIN_SALARY_RUB", "200000"))
JOBHUNT_MIN_SALARY_USD = int(os.environ.get("JOBHUNT_MIN_SALARY_USD", "3000"))
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

JOBHUNT_HIRIFY_ENABLED = os.environ.get("JOBHUNT_HIRIFY_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_HIRIFY_QUERY = os.environ.get("JOBHUNT_HIRIFY_QUERY", "frontend react typescript")
JOBHUNT_HIRIFY_QUERIES = os.environ.get("JOBHUNT_HIRIFY_QUERIES", "").strip()
JOBHUNT_HIRIFY_MAX_PAGES = int(os.environ.get("JOBHUNT_HIRIFY_MAX_PAGES", "2"))

JOBHUNT_HIREHI_ENABLED = os.environ.get("JOBHUNT_HIREHI_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_HIREHI_SUBCATEGORIES = os.environ.get("JOBHUNT_HIREHI_SUBCATEGORIES", "frontend,fullstack")
JOBHUNT_HIREHI_MAX_PAGES = int(os.environ.get("JOBHUNT_HIREHI_MAX_PAGES", "2"))
JOBHUNT_HIREHI_LIMIT = int(os.environ.get("JOBHUNT_HIREHI_LIMIT", "50"))

JOBHUNT_TG_ENABLED = os.environ.get("JOBHUNT_TG_ENABLED", "true").lower() in ("true", "1", "yes")
JOBHUNT_TG_CHANNELS = os.environ.get(
    "JOBHUNT_TG_CHANNELS",
    "frontend_rabota,job_react,proglib_jobs",
)
JOBHUNT_TG_KEYWORDS = os.environ.get(
    "JOBHUNT_TG_KEYWORDS",
    "frontend,front-end,react,typescript,next.js,nextjs,javascript,fullstack,full-stack,фронтенд,фронт",
)


def hirify_search_queries() -> list[str]:
    if JOBHUNT_HIRIFY_QUERIES:
        parts = [q.strip() for q in JOBHUNT_HIRIFY_QUERIES.split(",") if q.strip()]
        if parts:
            return parts
    return [JOBHUNT_HIRIFY_QUERY]


def hirehi_subcategories() -> list[str]:
    parts = [s.strip() for s in JOBHUNT_HIREHI_SUBCATEGORIES.split(",") if s.strip()]
    return parts or ["frontend"]


def tg_channel_names() -> list[str]:
    return [c.strip().lstrip("@") for c in JOBHUNT_TG_CHANNELS.split(",") if c.strip()]


def tg_match_keywords() -> tuple[str, ...]:
    return tuple(k.strip().lower() for k in JOBHUNT_TG_KEYWORDS.split(",") if k.strip())


# --- Resume sync (HH / Habr / LinkedIn) ---

JOBHUNT_RESUME_SYNC_ENABLED = os.environ.get(
    "JOBHUNT_RESUME_SYNC_ENABLED", "false"
).lower() in ("true", "1", "yes")
JOBHUNT_RESUME_AUTO_SYNC = os.environ.get(
    "JOBHUNT_RESUME_AUTO_SYNC", "false"
).lower() in ("true", "1", "yes")

HH_CLIENT_ID = os.environ.get("HH_CLIENT_ID", "").strip()  # deprecated — applicant API closed 2025-12-15
HH_CLIENT_SECRET = os.environ.get("HH_CLIENT_SECRET", "").strip()
HH_ACCESS_TOKEN = os.environ.get("HH_ACCESS_TOKEN", "").strip()
HH_REFRESH_TOKEN = os.environ.get("HH_REFRESH_TOKEN", "").strip()
HH_RESUME_ID = os.environ.get("HH_RESUME_ID", "").strip()
HH_PUBLISH_AFTER_SYNC = os.environ.get("HH_PUBLISH_AFTER_SYNC", "false").lower() in (
    "true",
    "1",
    "yes",
)

HABR_SESSION_COOKIE = os.environ.get("HABR_SESSION_COOKIE", "").strip()
HABR_PROFILE_SLUG = os.environ.get("HABR_PROFILE_SLUG", "").strip()

LINKEDIN_LI_AT = os.environ.get("LINKEDIN_LI_AT", "").strip()
LINKEDIN_JSESSIONID = os.environ.get("LINKEDIN_JSESSIONID", "").strip()
LINKEDIN_SYNC_ENABLED = os.environ.get("LINKEDIN_SYNC_ENABLED", "false").lower() in (
    "true",
    "1",
    "yes",
)
