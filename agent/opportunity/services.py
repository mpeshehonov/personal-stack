"""Glue: upsert opportunity from job lead, scan hooks, ideas."""

from __future__ import annotations

import json
import logging
from typing import Any

from opportunity.actions import decide_next_action
from opportunity.ideas import ensure_strategic_ideas
from opportunity.migrate import ensure_migrated_on_startup
from opportunity.models import LEGACY_STATUS_TO_OPP, OpportunityStatus
from opportunity.profile import ensure_profile
from opportunity.repository import upsert_job_opportunity
from opportunity.scoring import score_opportunity

logger = logging.getLogger(__name__)


def upsert_from_job_lead(
    *,
    lead_id: int,
    vacancy: dict[str, Any],
    match_score: int,
    match_reasons: list[str],
    lead_status: str = "new",
) -> int:
    """Create/update JOB opportunity linked to job_leads.id."""
    ensure_profile()
    bundle = score_opportunity(
        vacancy, match_score=match_score, match_reasons=match_reasons
    )
    scores = bundle.to_dict()
    source = vacancy.get("_source") or vacancy.get("source") or ""
    company = (
        (vacancy.get("employer") or {}).get("name")
        or vacancy.get("company")
        or ""
    )
    paywall = bool(vacancy.get("_paywall")) or (
        str(source).startswith("hirify") and vacancy.get("_actionable") is not True
    )
    # Default hirify → paywall-ish unless explicitly actionable
    if str(source) == "hirify" and vacancy.get("_actionable") is None:
        paywall = True

    # Aggregator TG boards (Runello/gmatch): never treat bot-apply as actionable
    if vacancy.get("_aggregator") and vacancy.get("_actionable") is not True:
        paywall = True

    apply_path = vacancy.get("_apply_path") or {}
    analysis = {
        "match_score": match_score,
        "match_reasons": match_reasons,
        "actionable": (not paywall) and vacancy.get("_actionable", True) is not False,
        "paywall": paywall,
        "published_at": vacancy.get("_published_at") or vacancy.get("published_at"),
        "age_days": None,
        "aggregator": bool(vacancy.get("_aggregator") or apply_path.get("aggregator")),
        "apply_strategy": apply_path.get("strategy")
        or (
            "research_company"
            if paywall
            else ("direct_url" if vacancy.get("_actionable") else "weak")
        ),
        "apply_hint_ru": vacancy.get("_apply_hint_ru")
        or apply_path.get("apply_hint_ru")
        or "",
        "apply_contacts": {
            "telegrams": list(apply_path.get("telegrams") or []),
            "emails": list(apply_path.get("emails") or []),
            "direct_urls": list(apply_path.get("direct_urls") or []),
        },
        "company": str(company),
    }
    try:
        from opportunity.scoring import _vacancy_age_days

        analysis["age_days"] = _vacancy_age_days(vacancy)
    except Exception:
        pass

    opp_status = LEGACY_STATUS_TO_OPP.get(
        lead_status, OpportunityStatus.NEW
    ).value
    next_action, priority = decide_next_action(
        status=opp_status, scores=scores, analysis=analysis
    )
    return upsert_job_opportunity(
        job_lead_id=lead_id,
        title=vacancy.get("name") or vacancy.get("title") or "",
        company=str(company),
        source=str(source),
        source_url=str(vacancy.get("alternate_url") or vacancy.get("url") or ""),
        status=opp_status,
        raw_payload={
            "id": vacancy.get("id"),
            "source": source,
        },
        normalized_payload={
            "name": vacancy.get("name"),
            "employer": vacancy.get("employer"),
            "salary": vacancy.get("salary"),
            "schedule": vacancy.get("schedule"),
            "snippet": vacancy.get("snippet"),
            "_source": source,
            "_published_at": vacancy.get("_published_at"),
            "_paywall": paywall,
            "_actionable": analysis["actionable"],
        },
        scores=scores,
        analysis=analysis,
        next_action=next_action,
        next_action_priority=priority,
        overall_score=bundle.overall,
    )


def after_scan_hook(summary: dict[str, Any]) -> dict[str, Any]:
    """Called after scan_and_store_leads — migration + all verticals."""
    ensure_migrated_on_startup()
    ideas = ensure_strategic_ideas()
    from opportunity.client_scan import ensure_client_orders
    from opportunity.verticals import ensure_vertical_opportunities

    clients = ensure_client_orders()
    verticals = ensure_vertical_opportunities()
    summary = dict(summary)
    summary["opportunity"] = {
        "ideas_upserted": ideas.get("upserted", 0),
        "ideas": ideas.get("titles", []),
        "client_orders": clients.get("kept", 0),
        "client_titles": clients.get("titles", []),
        "verticals": verticals.get("by_type", {}),
        "vertical_titles": verticals.get("titles", []),
    }
    return summary


def ensure_all_opportunities() -> dict[str, Any]:
    """Manual/brief entry: migrate jobs + verticals + legacy OTHER ideas."""
    ensure_migrated_on_startup()
    ideas = ensure_strategic_ideas()
    from opportunity.client_scan import ensure_client_orders
    from opportunity.verticals import ensure_vertical_opportunities

    clients = ensure_client_orders()
    verticals = ensure_vertical_opportunities()
    return {"ideas": ideas, "clients": clients, "verticals": verticals}


def lead_fields_vacancy_from_stored(
    fields: dict[str, Any], vacancy: dict[str, Any]
) -> dict[str, Any]:
    """Merge stored lead field dict with original vacancy for scoring."""
    merged = dict(vacancy)
    if not merged.get("name") and fields.get("title"):
        merged["name"] = fields["title"]
    return merged
