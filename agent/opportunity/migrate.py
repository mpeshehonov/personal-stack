"""Schema migrate + backfill job_leads → opportunities; Hirify repair."""

from __future__ import annotations

import json
import logging
from typing import Any

from orchestrator.state import get_conn, get_job_source, list_job_leads, set_job_source
from opportunity.actions import decide_next_action
from opportunity.models import LEGACY_STATUS_TO_OPP, OpportunityStatus
from opportunity.profile import ensure_profile
from opportunity.repository import (
    count_opportunities,
    ensure_opportunity_schema,
    get_opportunity_by_lead,
    upsert_job_opportunity,
)
from opportunity.scoring import lead_row_to_vacancy_shape, score_opportunity

logger = logging.getLogger(__name__)


def migrate_opportunity_core(*, rescore: bool = True, repair_hirify: bool = True) -> dict[str, Any]:
    ensure_profile()
    ensure_opportunity_schema()

    hirify_fix: dict[str, Any] = {}
    if repair_hirify:
        hirify_fix = repair_hirify_source()

    # Backfill all leads (status=None)
    leads = list_job_leads(status=None, limit=10000, min_score=0)
    created = 0
    updated = 0
    for row in leads:
        existing = get_opportunity_by_lead(int(row["id"]))
        vacancy = lead_row_to_vacancy_shape(row)
        match_score = int(row["match_score"] or 0)
        try:
            reasons = json.loads(row["match_reasons_json"] or "[]")
        except json.JSONDecodeError:
            reasons = []

        if rescore:
            bundle = score_opportunity(
                vacancy, match_score=match_score, match_reasons=reasons
            )
            scores = bundle.to_dict()
            overall = bundle.overall
        else:
            scores = {
                "fit": {"score": match_score, "reasons": reasons},
                "overall_score": match_score,
            }
            overall = match_score

        legacy_status = row["status"] or "new"
        opp_status = LEGACY_STATUS_TO_OPP.get(
            legacy_status, OpportunityStatus.NEW
        ).value
        analysis = {
            "match_score": match_score,
            "match_reasons": reasons,
            "actionable": vacancy.get("_actionable", True),
            "paywall": vacancy.get("_paywall", False),
            "migrated_from_lead": True,
        }
        next_action, priority = decide_next_action(
            status=opp_status, scores=scores, analysis=analysis
        )
        oid = upsert_job_opportunity(
            job_lead_id=int(row["id"]),
            title=row["title"],
            company=row["company"] or "",
            source=row["source"],
            source_url=row["url"] or "",
            status=opp_status,
            raw_payload={"lead_id": row["id"], "ts": row["ts"]},
            normalized_payload=vacancy,
            scores=scores,
            analysis=analysis,
            next_action=next_action,
            next_action_priority=priority,
            overall_score=overall,
        )
        if existing:
            updated += 1
        else:
            created += 1
            _ = oid

    return {
        "leads_seen": len(leads),
        "created": created,
        "updated": updated,
        "opportunities_total": count_opportunities(),
        "hirify": hirify_fix,
    }


def repair_hirify_source() -> dict[str, Any]:
    """
    Re-enable Hirify if disabled by paywall-driven dislikes.
    Preserve weight floor at 1.0 when re-enabling.
    """
    row = get_job_source("hirify")
    if row is None:
        set_job_source(
            "hirify",
            kind="board",
            weight=1.2,
            enabled=True,
            status="active",
            notes="Opportunity OS: Hirify = high relevance; paywall ≠ bad source",
        )
        return {"action": "seeded", "weight": 1.2, "enabled": True}

    enabled = bool(row["enabled"]) and row["status"] == "active"
    weight = float(row["weight"])
    if enabled and weight >= 0.9:
        return {"action": "noop", "weight": weight, "enabled": True}

    new_w = max(weight, 1.2)
    set_job_source(
        "hirify",
        kind=row["kind"] or "board",
        weight=new_w,
        enabled=True,
        status="active",
        notes=(
            (row["notes"] or "")
            + " | repaired: paywall dislikes must not disable Hirify"
        ).strip(" |"),
    )
    logger.info("Hirify source repaired: weight %.2f → %.2f, enabled", weight, new_w)
    return {"action": "repaired", "weight_before": weight, "weight_after": new_w, "enabled": True}


def ensure_migrated_on_startup() -> None:
    """Idempotent hook from init_db / first scan."""
    try:
        ensure_opportunity_schema()
        ensure_profile()
        with get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM opportunities").fetchone()
            opp_c = int(row["c"] if row else 0)
            lead_c = conn.execute("SELECT COUNT(*) AS c FROM job_leads").fetchone()
            leads = int(lead_c["c"] if lead_c else 0)
        if leads > 0 and opp_c < leads:
            logger.info(
                "Backfilling opportunities (%s leads, %s opps)", leads, opp_c
            )
            migrate_opportunity_core(rescore=True, repair_hirify=True)
        else:
            repair_hirify_source()
    except Exception:
        logger.exception("Opportunity migrate on startup failed")
