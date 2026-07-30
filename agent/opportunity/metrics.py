"""Opportunity OS quality metrics — no claims without data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from opportunity.repository import (
    funnel_counts,
    list_opportunity_feedback,
    list_opportunities,
    save_metrics_day,
)
from orchestrator.state import get_conn, list_job_sources


def compute_funnel_snapshot() -> dict[str, int]:
    raw = funnel_counts()
    return {
        "new": int(raw.get("new", 0)),
        "saved": int(raw.get("saved", 0)),
        "applied": int(raw.get("applied", 0)),
        "interview": int(raw.get("interview", 0)),
        "offer": int(raw.get("offer", 0)),
        "rejected": int(raw.get("rejected", 0)),
        "skipped": int(raw.get("skipped", 0)),
        "hired": int(raw.get("hired", 0)),
        "archived": int(raw.get("archived", 0)),
    }


def compute_metrics(scan_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    scan_summary = scan_summary or {}
    funnel = compute_funnel_snapshot()
    feedback = list_opportunity_feedback(limit=1000)
    shown = list_opportunities(status=None, opp_type="JOB", limit=500, min_overall=0)

    liked = sum(1 for f in feedback if f["action"] in ("LIKE", "SAVE"))
    applied = sum(1 for f in feedback if f["action"] == "APPLY")
    interview = sum(1 for f in feedback if f["action"] == "INTERVIEW")
    offer = sum(1 for f in feedback if f["action"] == "OFFER")
    shown_n = len(shown)
    feedback_n = len(feedback)

    # precision@5: among top-5 new by overall, share with LIKE/SAVE/APPLY feedback
    top5 = list_opportunities(status="new", opp_type="JOB", limit=5, min_overall=0)
    top5_ids = {o.id for o in top5}
    positive_on_top = 0
    judged_top = 0
    fb_by_opp: dict[int, str] = {}
    for f in feedback:
        oid = int(f["opportunity_id"])
        if oid not in fb_by_opp:
            fb_by_opp[oid] = f["action"]
    for oid in top5_ids:
        if oid in fb_by_opp:
            judged_top += 1
            if fb_by_opp[oid] in ("LIKE", "SAVE", "APPLY", "INTERVIEW"):
                positive_on_top += 1
    precision_at_5 = (
        round(positive_on_top / judged_top, 3) if judged_top else None
    )

    apply_rate = round(applied / liked, 3) if liked else None
    interview_rate = round(interview / applied, 3) if applied else None
    feedback_coverage = (
        round(feedback_n / shown_n, 3) if shown_n else None
    )

    source_quality: dict[str, Any] = {}
    for row in list_job_sources():
        source_quality[row["source_key"]] = {
            "weight": round(float(row["weight"]), 3),
            "enabled": bool(row["enabled"]),
            "status": row["status"],
        }

    metrics = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source_count": len(source_quality),
        "raw_signals": int(scan_summary.get("fetched") or 0),
        "deduplicated": int(scan_summary.get("skipped_duplicates") or 0)
        + int(scan_summary.get("skipped_existing") or 0),
        "filtered": int(scan_summary.get("below_threshold") or 0),
        "scored": int(scan_summary.get("new_count") or 0),
        "shown_to_user": shown_n,
        "liked": liked,
        "saved": funnel.get("saved", 0),
        "applied": applied,
        "interview": interview,
        "offer": offer,
        "precision_at_5": precision_at_5,
        "precision_at_5_note": (
            "null until top-5 items receive feedback"
            if precision_at_5 is None
            else "based on latest feedback per opp"
        ),
        "apply_rate": apply_rate,
        "interview_rate": interview_rate,
        "feedback_coverage": feedback_coverage,
        "source_quality": source_quality,
        "funnel": funnel,
        "insufficient_data": precision_at_5 is None or apply_rate is None,
    }
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    save_metrics_day(day, metrics)
    return metrics


def format_metrics_plain(metrics: dict[str, Any] | None = None) -> str:
    m = metrics or compute_metrics()
    lines = [
        "Opportunity metrics",
        f"raw={m.get('raw_signals')} filtered={m.get('filtered')} scored={m.get('scored')}",
        f"shown={m.get('shown_to_user')} liked={m.get('liked')} applied={m.get('applied')} "
        f"interview={m.get('interview')}",
        f"precision@5={m.get('precision_at_5')} apply_rate={m.get('apply_rate')} "
        f"interview_rate={m.get('interview_rate')} coverage={m.get('feedback_coverage')}",
    ]
    if m.get("insufficient_data"):
        lines.append("⚠ Недостаточно данных — не заявляем «стало лучше».")
    return "\n".join(lines)
