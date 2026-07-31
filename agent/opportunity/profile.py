"""Versioned opportunity profile — editable, not hardcoded in matcher."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.config import MEMORY_DIR, SITE_DIR

logger = logging.getLogger(__name__)

PROFILE_PATH = MEMORY_DIR / "opportunity_profile.json"
RESUME_PATH = SITE_DIR / "content" / "resume" / "resume.json"

DEFAULT_WEIGHTS: dict[str, float] = {
    "fit": 0.30,
    "income": 0.20,
    "growth": 0.10,
    "probability": 0.15,
    "strategic": 0.15,
    "urgency": 0.10,
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_profile() -> dict[str, Any]:
    skills: list[str] = []
    if RESUME_PATH.exists():
        try:
            data = json.loads(RESUME_PATH.read_text(encoding="utf-8"))
            skills = [str(s) for s in data.get("skills", []) if str(s).strip()]
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not read resume skills for profile: %s", exc)

    return {
        "version": 1,
        "updated_at": _utcnow(),
        "target_income_usd_month": 3500,
        "min_income_usd_month": 3000,
        "min_income_rub_month": 200000,
        "target_roles": [
            "Senior Frontend Engineer",
            "Senior React Engineer",
            "Frontend Lead",
        ],
        "primary_stack": [
            "React",
            "TypeScript",
            "Next.js",
            "JavaScript",
            "REST API",
            "CI/CD",
        ],
        "adjacent_roles": [
            "Fullstack (React-heavy)",
            "React Native / Expo",
            "Product Engineer (frontend)",
        ],
        "desired_company_types": [
            "product",
            "fintech",
            "ecommerce",
            "b2b saas",
            "cybersecurity product",
        ],
        "geography": ["remote", "RF remote", "CIS remote"],
        "remote_preference": "remote_only",
        "work_formats": ["full-time", "contract_ok"],
        "career_goals": [
            "Stabilize income ASAP",
            "Own a frontend module from API to release",
            "Keep senior React/Next positioning",
        ],
        "strategic_interests": [
            "React Native / Expo POS & mobile",
            "Canvas / complex editors",
            "Web3 / TON wallets (portfolio signal)",
            "Streamer / creator tooling",
            "Seat-map / ticketing niche",
        ],
        "undesired": [
            "junior",
            "intern",
            "office_only_moscow",
            "pure_vue_without_react",
            "angular_primary",
            "bitrix",
            "agency_mass_hiring",
            "digest_aggregates",
        ],
        "resume_skills": skills,
        "score_weights": dict(DEFAULT_WEIGHTS),
        "preference_adjustments": {},
        "client_targets": [],
        "network_contacts": [],
        "owned_product_assets": [],
        "product_ideas_blocked": [
            "sendonate",
            "preeglos",
            "x5",
            "citilink",
            "potalonu",
            "bi.zone",
            "nlmk",
            "rostelecom",
            "sbertech",
            "zenit",
            "baucenter",
            "maximaster",
            "akvaprom",
        ],
        "notes": {
            "hirify": (
                "Hirify is high-relevance; many cards need Hirify Plus for contacts. "
                "Treat paywall skips as actionability, not source quality."
            ),
            "comp": "Public resume omits salary; rails are private negotiation.",
            "product_ip": (
                "Never package employer/client case studies from the site. "
                "Only owned_product_assets with can_resell=true. "
                "Net-new PRODUCT ideas use analysis.kind=net_new."
            ),
        },
    }


def ensure_profile() -> dict[str, Any]:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PROFILE_PATH.exists():
        profile = default_profile()
        save_profile(profile)
        return profile
    return load_profile()


def load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        return ensure_profile()
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    base = default_profile()
    base.update(data)
    # Keep weights complete
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(data.get("score_weights") or {})
    base["score_weights"] = weights
    if not base.get("resume_skills"):
        base["resume_skills"] = default_profile()["resume_skills"]
    return base


def save_profile(profile: dict[str, Any]) -> Path:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = deepcopy(profile)
    out["updated_at"] = _utcnow()
    out["version"] = int(out.get("version") or 1)
    PROFILE_PATH.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return PROFILE_PATH


def update_profile_fields(**fields: Any) -> dict[str, Any]:
    profile = load_profile()
    for key, value in fields.items():
        if key == "score_weights" and isinstance(value, dict):
            weights = dict(profile.get("score_weights") or DEFAULT_WEIGHTS)
            weights.update(value)
            profile["score_weights"] = weights
        else:
            profile[key] = value
    save_profile(profile)
    return profile


def format_profile_plain(profile: dict[str, Any] | None = None) -> str:
    p = profile or load_profile()
    lines = [
        f"Opportunity profile v{p.get('version')} (updated {p.get('updated_at', '')[:19]})",
        f"Target income: ${p.get('target_income_usd_month')}/mo "
        f"(min ${p.get('min_income_usd_month')} / {p.get('min_income_rub_month')} RUB)",
        f"Roles: {', '.join(p.get('target_roles') or [])}",
        f"Stack: {', '.join(p.get('primary_stack') or [])}",
        f"Remote: {p.get('remote_preference')}",
        f"Undesired: {', '.join(p.get('undesired') or [])}",
        "",
        "Edit: agent/memory/opportunity_profile.json or /profile set <key>=<value>",
    ]
    return "\n".join(lines)
