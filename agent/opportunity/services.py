"""Glue: upsert opportunity from job lead, scan hooks, ideas."""

from __future__ import annotations

import json
import logging
from typing import Any

from job_hunt.company_research import research_direct_apply, research_hint_ru
from opportunity.actions import decide_next_action
from opportunity.ideas import ensure_strategic_ideas
from opportunity.migrate import ensure_migrated_on_startup
from opportunity.models import LEGACY_STATUS_TO_OPP, OpportunityStatus
from opportunity.profile import ensure_profile
from opportunity.repository import upsert_job_opportunity
from opportunity.scoring import score_opportunity

logger = logging.getLogger(__name__)


def enrich_apply_research(
    analysis: dict[str, Any],
    *,
    title: str = "",
    live_hh: bool = True,
) -> dict[str, Any]:
    """Attach HH/career research; upgrade to direct_url when HH vacancy found."""
    analysis = dict(analysis or {})
    company = str(analysis.get("company") or "").strip()
    needs = (
        analysis.get("aggregator")
        or analysis.get("apply_strategy") in ("research_company", "weak")
        or analysis.get("actionable") is False
        or analysis.get("paywall")
    )
    if not needs and analysis.get("research"):
        return analysis

    research = research_direct_apply(company, title=title, live_hh=live_hh and bool(company))
    analysis["research"] = research

    contacts = dict(analysis.get("apply_contacts") or {})
    direct = list(contacts.get("direct_urls") or [])
    if research.get("hh_vacancy_url"):
        direct = [research["hh_vacancy_url"]] + [u for u in direct if u != research["hh_vacancy_url"]]
        contacts["direct_urls"] = direct
        analysis["apply_contacts"] = contacts
        analysis["actionable"] = True
        analysis["paywall"] = False
        analysis["apply_strategy"] = "direct_url"
        analysis["apply_hint_ru"] = research_hint_ru(research)
    else:
        hint = research_hint_ru(research)
        if hint:
            analysis["apply_hint_ru"] = hint
        elif company:
            analysis["apply_hint_ru"] = (
                f"Не через агрегатор. «{company}»: HH / карьерный сайт / LinkedIn HR → "
                "мыло или TG в личку"
            )
    return analysis


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

    # Aggregator / no contacts → hunt HH employer + career search links
    title = vacancy.get("name") or vacancy.get("title") or ""
    if (
        analysis.get("aggregator")
        or analysis.get("apply_strategy") in ("research_company", "weak")
        or not analysis.get("actionable")
    ):
        analysis = enrich_apply_research(
            analysis,
            title=str(title),
            live_hh=bool(str(company).strip()),
        )

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


def refresh_research_for_opportunities(*, limit: int = 12) -> int:
    """Backfill HH/career research on open JOB cards that still lack it."""
    from job_hunt.apply_path import extract_company_name
    from opportunity.actions import decide_next_action
    from opportunity.repository import list_opportunities, update_opportunity_analysis
    from orchestrator.state import get_job_lead

    rows = list_opportunities(
        status=OpportunityStatus.NEW.value,
        opp_type="JOB",
        limit=40,
        min_overall=60,
    )
    updated = 0
    for opp in rows[:limit]:
        analysis = dict(opp.analysis or {})
        if analysis.get("research") and (
            analysis["research"].get("hh_vacancy_url")
            or analysis["research"].get("hh_search_url")
            or analysis["research"].get("career_search_url")
        ):
            # Already researched enough; skip heavy HH unless still aggregator w/o HH hit
            if not (
                analysis.get("aggregator")
                and not analysis["research"].get("hh_vacancy_url")
                and not analysis.get("_research_attempted")
            ):
                continue

        company = (opp.company_or_entity or analysis.get("company") or "").strip()
        if (not company or company in ("—", "-")) and opp.job_lead_id:
            lead = get_job_lead(int(opp.job_lead_id))
            if lead:
                company = extract_company_name(lead["description_snippet"] or "") or company
                if company:
                    analysis["company"] = company

        analysis["_research_attempted"] = True
        analysis = enrich_apply_research(
            analysis,
            title=opp.title or "",
            live_hh=bool(company),
        )
        scores = opp.scores or {}
        if "overall_score" not in scores:
            scores = {**scores, "overall_score": opp.overall_score}
        next_action, priority = decide_next_action(
            status=opp.status.value if hasattr(opp.status, "value") else str(opp.status),
            scores=scores,
            analysis=analysis,
        )
        update_opportunity_analysis(
            int(opp.id),
            analysis,
            next_action=next_action,
            next_action_priority=priority,
            company_or_entity=company or None,
        )
        updated += 1
    return updated


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
