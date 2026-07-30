"""Opportunity-level feedback + gated source-weight updates."""

from __future__ import annotations

import logging
import re
from typing import Any

from job_hunt.sources import (
    DELTA,
    WEIGHT_FLOOR_DISABLE,
    WEIGHT_MAX,
    WEIGHT_MIN,
    ensure_default_sources,
    source_key_for_lead,
)
from orchestrator.state import (
    add_job_feedback,
    get_job_lead,
    get_job_source,
    set_job_source,
    update_job_lead_status,
    update_source_weight,
)
from opportunity.actions import decide_next_action
from opportunity.models import (
    FEEDBACK_TO_STATUS,
    LEGACY_FEEDBACK_TO_OPP,
    NON_SOURCE_PUNISH_REASONS,
    FeedbackAction,
)
from opportunity.preferences import rebuild_preferences
from opportunity.repository import (
    add_opportunity_feedback,
    get_opportunity,
    get_opportunity_by_lead,
    update_opportunity_status,
)

logger = logging.getLogger(__name__)


def _is_non_punish_reason(reason: str) -> bool:
    text = (reason or "").lower()
    if not text:
        return False
    for token in NON_SOURCE_PUNISH_REASONS:
        if token in text:
            return True
    return False


def _normalize_action(action: str) -> FeedbackAction:
    raw = (action or "").strip()
    upper = raw.upper()
    try:
        return FeedbackAction(upper)
    except ValueError:
        pass
    legacy = LEGACY_FEEDBACK_TO_OPP.get(raw.lower())
    if legacy:
        return legacy
    # pass / мимо
    if raw.lower() in ("pass", "мимо"):
        return FeedbackAction.DISLIKE
    raise ValueError(f"unknown feedback action: {action}")


def apply_opportunity_feedback(
    *,
    opportunity_id: int | None = None,
    lead_id: int | None = None,
    action: str,
    reason: str = "",
) -> dict[str, Any]:
    """
    Record opportunity feedback, sync legacy lead status, optionally adjust source weight.

    Paywall / not_actionable reasons do NOT reduce source weight (Hirify fix).
    """
    fb = _normalize_action(action)
    opp = None
    if opportunity_id is not None:
        opp = get_opportunity(opportunity_id)
    elif lead_id is not None:
        opp = get_opportunity_by_lead(lead_id)
        if opp is None and lead_id is not None:
            # Lazy: feedback on lead before migration — still write job_feedback
            return _legacy_only_feedback(lead_id, fb, reason)

    if opp is None:
        raise KeyError("opportunity not found")

    lead_id = opp.job_lead_id
    add_opportunity_feedback(
        int(opp.id),
        fb.value,
        reason=reason,
        meta={"lead_id": lead_id},
    )

    new_status = FEEDBACK_TO_STATUS.get(fb)
    next_action = None
    priority = None
    if new_status:
        scores = opp.scores or {}
        analysis = opp.analysis or {}
        next_action, priority = decide_next_action(
            status=new_status,
            scores=scores,
            analysis=analysis,
        )
        update_opportunity_status(
            int(opp.id),
            new_status.value,
            next_action=next_action,
            next_action_priority=priority,
        )

    # Sync legacy lead
    source_result: dict[str, Any] = {}
    if lead_id:
        lead = get_job_lead(lead_id)
        if lead is not None:
            legacy_action = {
                FeedbackAction.LIKE: "like",
                FeedbackAction.DISLIKE: "dislike",
                FeedbackAction.APPLY: "applied",
                FeedbackAction.INTERVIEW: "interview",
                FeedbackAction.SAVE: "like",
                FeedbackAction.SKIP: "dislike",
                FeedbackAction.NOT_RELEVANT: "dislike",
            }.get(fb)
            if legacy_action:
                source_key = source_key_for_lead(lead)
                ensure_default_sources()
                if get_job_source(source_key) is None:
                    kind = "telegram" if source_key.startswith("tg:") else "board"
                    set_job_source(
                        source_key,
                        kind=kind,
                        weight=1.0,
                        enabled=True,
                        status="active",
                    )
                add_job_feedback(
                    lead_id,
                    action=legacy_action,
                    note=reason,
                    source_key=source_key,
                )
                # Status mapping for lead
                lead_status = {
                    "like": "liked",
                    "dislike": "rejected",
                    "applied": "applied",
                    "interview": "interview",
                }.get(legacy_action)
                if lead_status:
                    update_job_lead_status(lead_id, lead_status)

                skip_source_penalty = (
                    fb in (FeedbackAction.NOT_RELEVANT, FeedbackAction.SKIP)
                    and _is_non_punish_reason(reason)
                ) or (
                    legacy_action == "dislike" and _is_non_punish_reason(reason)
                )

                row = get_job_source(source_key)
                old_w = float(row["weight"]) if row else 1.0
                new_w = old_w
                disabled = False
                if skip_source_penalty:
                    source_result = {
                        "source_key": source_key,
                        "weight_before": round(old_w, 3),
                        "weight_after": round(old_w, 3),
                        "disabled": False,
                        "source_weight_skipped": True,
                        "skip_reason": "actionability/paywall — source relevance preserved",
                    }
                else:
                    delta = DELTA.get(legacy_action, 0.0)
                    new_w = max(WEIGHT_MIN, min(WEIGHT_MAX, old_w + delta))
                    if legacy_action == "dislike" and new_w < WEIGHT_FLOOR_DISABLE:
                        update_source_weight(source_key, new_w, enabled=False)
                        disabled = True
                    elif delta:
                        update_source_weight(source_key, new_w)
                    source_result = {
                        "source_key": source_key,
                        "weight_before": round(old_w, 3),
                        "weight_after": round(new_w, 3),
                        "disabled": disabled,
                        "source_weight_skipped": False,
                    }

    pref = rebuild_preferences()
    return {
        "opportunity_id": opp.id,
        "lead_id": lead_id,
        "action": fb.value,
        "reason": reason,
        "status": new_status.value if new_status else opp.status.value,
        "next_action": next_action,
        "next_action_priority": priority,
        "source": source_result,
        "preferences": {
            "updated": pref.get("updated"),
            "samples": pref.get("samples"),
            "explanations": (pref.get("explanations") or [])[:3],
        },
        "title": opp.title,
        "company": opp.company_or_entity,
    }


def _legacy_only_feedback(lead_id: int, fb: FeedbackAction, reason: str) -> dict[str, Any]:
    """Fallback when opportunity row missing — preserve old apply_feedback behavior with paywall gate."""
    from job_hunt.sources import apply_feedback as legacy_apply

    legacy = {
        FeedbackAction.LIKE: "like",
        FeedbackAction.DISLIKE: "dislike",
        FeedbackAction.APPLY: "applied",
        FeedbackAction.INTERVIEW: "interview",
        FeedbackAction.SAVE: "like",
        FeedbackAction.SKIP: "dislike",
        FeedbackAction.NOT_RELEVANT: "dislike",
    }.get(fb, "dislike")

    if legacy == "dislike" and _is_non_punish_reason(reason):
        lead = get_job_lead(lead_id)
        if lead is None:
            raise KeyError(f"lead {lead_id} not found")
        source_key = source_key_for_lead(lead)
        add_job_feedback(lead_id, action="dislike", note=reason or "paywall", source_key=source_key)
        update_job_lead_status(lead_id, "rejected")
        row = get_job_source(source_key)
        w = float(row["weight"]) if row else 1.0
        return {
            "opportunity_id": None,
            "lead_id": lead_id,
            "action": fb.value,
            "reason": reason,
            "source": {
                "source_key": source_key,
                "weight_before": w,
                "weight_after": w,
                "disabled": False,
                "source_weight_skipped": True,
            },
            "title": lead["title"],
            "company": lead["company"],
        }

    result = legacy_apply(lead_id, legacy, note=reason)
    result["opportunity_id"] = None
    result["action"] = fb.value
    return result


def infer_paywall_reason_from_note(note: str) -> str:
    text = (note or "").lower()
    if re.search(r"plus|подписк|контакт|paywall|невозможн", text):
        return note or "paywall"
    return note
