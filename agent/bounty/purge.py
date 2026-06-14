"""Reject non-submit bounty drafts and re-validate pending queue."""

from __future__ import annotations

import logging
import re

from bounty.models import BountyFinding
from bounty.validator import validate_finding
from orchestrator.state import get_bounty_draft_meta, list_bounty_drafts, update_bounty_status

logger = logging.getLogger(__name__)

_HINT_TITLE = re.compile(r"^\[(Draft|Program)\]", re.I)


def _is_legacy_hint(row) -> bool:
    title = row["title"] or ""
    if _HINT_TITLE.search(title):
        return True
    if "GHSA-" in title or "Review GHSA" in title:
        return True
    if "Explore " in title and "HackerOne" in (row["body"] or ""):
        return True
    return False


def purge_non_submit_drafts(*, revalidate: bool = True) -> list[int]:
    """Auto-reject pending drafts that are hints or fail validation."""
    rejected: list[int] = []
    pending = list_bounty_drafts(status="pending", limit=50)

    for row in pending:
        draft_id = int(row["id"])
        meta = get_bounty_draft_meta(draft_id)
        if meta.get("kind") == "lead":
            continue

        reasons: list[str] = []
        if _is_legacy_hint(row):
            reasons.append("legacy hint draft")

        finding = BountyFinding.from_meta(meta)
        if not finding:
            if not reasons:
                reasons.append("нет structured submit-ready meta")
        elif revalidate:
            ok, val_reasons = validate_finding(finding)
            if not ok:
                reasons.extend(val_reasons)

        if reasons:
            update_bounty_status(draft_id, "rejected")
            rejected.append(draft_id)
            logger.info("Bounty purge #%s: %s", draft_id, "; ".join(reasons[:3]))

    return rejected
