"""Second-pass agent review for bounty findings."""

from __future__ import annotations

import json
import logging
import re

from bounty.config import BOUNTY_MIN_QUALITY_SCORE, BOUNTY_REVIEW_ENABLED
from bounty.models import BountyFinding
from bounty.programs import BountyProgram
from orchestrator.config import TASKS_DIR
from orchestrator.cursor_runner import run_cursor_prompt

logger = logging.getLogger(__name__)

_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)


def _load_review_template() -> str:
    return (TASKS_DIR / "bounty_review_prompt.md").read_text(encoding="utf-8")


def _parse_review(text: str) -> dict | None:
    for match in _JSON_BLOCK.finditer(text):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "approve" in data:
            return data
    return None


def review_finding(
    finding: BountyFinding,
    program: BountyProgram,
    *,
    research_summary: str = "",
) -> tuple[bool, int, list[str]]:
    """Agent QA pass. Returns (approved, quality_score, reject_reasons)."""
    if not BOUNTY_REVIEW_ENABLED:
        return True, 100, []

    payload = {
        k: finding.to_meta()[k]
        for k in (
            "title",
            "severity",
            "weakness_type",
            "asset",
            "impact",
            "reproduction_steps",
            "report_markdown",
        )
    }
    prompt = _load_review_template().format(
        program_name=program.name,
        platform=program.platform,
        program_url=program.url,
        research_summary=(research_summary or "—")[:2000],
        finding_json=json.dumps(payload, ensure_ascii=False, indent=2)[:12000],
        min_quality_score=BOUNTY_MIN_QUALITY_SCORE,
    )

    raw = run_cursor_prompt(prompt, one_shot=True)
    data = _parse_review(raw)
    if not data:
        logger.warning("Bounty review: no JSON verdict")
        return False, 0, ["reviewer не вернул JSON verdict"]

    score = int(data.get("quality_score") or 0)
    reasons = [str(r) for r in (data.get("reject_reasons") or []) if r]
    approve = bool(data.get("approve")) and bool(data.get("submit_ready"))
    if score < BOUNTY_MIN_QUALITY_SCORE:
        approve = False
        reasons.append(f"quality_score {score} < {BOUNTY_MIN_QUALITY_SCORE}")

    if not approve and not reasons:
        reasons.append("reviewer rejected without reasons")

    logger.info(
        "Bounty review %s: approve=%s score=%s",
        program.name,
        approve,
        score,
    )
    return approve, score, reasons
