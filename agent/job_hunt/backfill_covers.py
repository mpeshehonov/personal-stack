"""One-shot / CLI: draft covers and mark leads as applied (manual outreach sync)."""

from __future__ import annotations

import argparse
import json
import logging
from typing import Any

from job_hunt.drafter import draft_cover_letter
from job_hunt.sources import apply_feedback, source_key_for_lead
from orchestrator.state import (
    add_job_application,
    get_job_lead,
    init_db,
    update_job_lead_status,
)
from opportunity.services import upsert_from_job_lead
from opportunity.scoring import lead_row_to_vacancy_shape

logger = logging.getLogger(__name__)

# Canonical shortlist + brief "today" set user said they covered/applied
DEFAULT_APPLY_IDS = (42, 47, 45, 76, 43, 79)
# Cross-channel duplicates of the above
DEFAULT_DUPLICATE_IDS = (66, 59)  # 66→76 WB, 59→47 ЗЯ


def _lead_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "source": row["source"],
        "external_id": row["external_id"],
        "url": row["url"],
        "title": row["title"],
        "company": row["company"],
        "salary_raw": row["salary_raw"],
        "location": row["location"],
        "skills_json": row["skills_json"],
        "description_snippet": row["description_snippet"],
        "match_score": row["match_score"],
        "match_reasons_json": row["match_reasons_json"],
        "status": row["status"],
    }


def backfill_cover_and_apply(
    lead_ids: list[int],
    *,
    mark_applied: bool = True,
    channel: str = "hh",
) -> list[dict[str, Any]]:
    init_db()
    out: list[dict[str, Any]] = []
    for lead_id in lead_ids:
        row = get_job_lead(lead_id)
        if row is None:
            out.append({"lead_id": lead_id, "ok": False, "error": "missing"})
            continue
        lead = _lead_dict(row)
        try:
            reasons = json.loads(row["match_reasons_json"] or "[]")
        except json.JSONDecodeError:
            reasons = []
        vacancy = lead_row_to_vacancy_shape(row)
        upsert_from_job_lead(
            lead_id=lead_id,
            vacancy=vacancy,
            match_score=int(row["match_score"] or 0),
            match_reasons=reasons,
            lead_status=row["status"] or "new",
        )
        draft = draft_cover_letter(lead, channel=channel)  # type: ignore[arg-type]
        app_id = add_job_application(
            lead_id,
            cover_letter=draft["body"],
            status="draft",
            notes="backfill: user requested cover / applied outside bot",
        )
        if mark_applied:
            # Prefer opportunity path so statuses stay in sync
            try:
                apply_feedback(lead_id, "applied", note="backfill external apply + cover")
            except Exception:
                update_job_lead_status(lead_id, "applied")
        out.append(
            {
                "lead_id": lead_id,
                "ok": True,
                "company": row["company"],
                "title": row["title"],
                "application_id": app_id,
                "status": "applied" if mark_applied else row["status"],
                "source": source_key_for_lead(row),
            }
        )
    return out


def mark_duplicates(lead_ids: list[int], *, note: str) -> list[dict[str, Any]]:
    init_db()
    out = []
    for lead_id in lead_ids:
        row = get_job_lead(lead_id)
        if row is None:
            out.append({"lead_id": lead_id, "ok": False})
            continue
        try:
            apply_feedback(lead_id, "dislike", note=note)
        except Exception:
            update_job_lead_status(lead_id, "rejected")
        out.append({"lead_id": lead_id, "ok": True, "status": "rejected"})
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument("--ids", nargs="*", type=int, default=list(DEFAULT_APPLY_IDS))
    p.add_argument("--dupes", nargs="*", type=int, default=list(DEFAULT_DUPLICATE_IDS))
    p.add_argument("--no-apply", action="store_true")
    args = p.parse_args()
    covers = backfill_cover_and_apply(args.ids, mark_applied=not args.no_apply)
    dupes = mark_duplicates(
        args.dupes,
        note="bad_fit cross-channel duplicate — canonical cover on sibling lead",
    )
    print(json.dumps({"covers": covers, "dupes": dupes}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
