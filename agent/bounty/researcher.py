"""Run multi-stage bounty research for one program."""

from __future__ import annotations

import logging

from bounty.config import BOUNTY_REVIEW_ENABLED
from bounty.models import BountyFinding
from bounty.programs import BountyProgram
from bounty.report_parser import format_draft_body, parse_agent_finding
from bounty.reviewer import review_finding
from bounty.validator import validate_finding
from orchestrator.config import TASKS_DIR
from orchestrator.cursor_runner import run_cursor_prompt

logger = logging.getLogger(__name__)


def _load_prompt_template() -> str:
    path = TASKS_DIR / "bounty_research_prompt.md"
    return path.read_text(encoding="utf-8")


def build_research_prompt(program: BountyProgram) -> str:
    template = _load_prompt_template()
    return template.format(
        program_name=program.name,
        platform=program.platform,
        program_url=program.url,
        team_handle=program.team_handle,
        program_focus=program.focus,
        program_notes=program.notes or "—",
    )


def research_program(program: BountyProgram) -> tuple[BountyFinding | None, str]:
    """Research → auto-validate → optional agent review. Returns (finding, log)."""
    prompt = build_research_prompt(program)
    logger.info("Bounty deep research: %s (%s)", program.name, program.platform)
    raw = run_cursor_prompt(prompt, one_shot=True)
    research_summary = raw[:2500]

    finding = parse_agent_finding(raw, program)
    if not finding:
        return None, f"{program.name}: finding не прошёл parse gate"

    ok, reasons = validate_finding(finding)
    if not ok:
        logger.info("Bounty auto-reject %s: %s", program.name, reasons)
        return None, f"{program.name}: auto-reject — {'; '.join(reasons[:4])}"

    if BOUNTY_REVIEW_ENABLED:
        approved, score, review_reasons = review_finding(
            finding,
            program,
            research_summary=research_summary,
        )
        finding.quality_score = score
        if not approved:
            logger.info("Bounty review reject %s: %s", program.name, review_reasons)
            return None, (
                f"{program.name}: review reject (score {score}) — "
                f"{'; '.join(review_reasons[:4])}"
            )
        logger.info("Bounty finding approved: %s (score %s)", finding.title[:60], score)

    return finding, f"{program.name}: submit-ready — {finding.title[:80]}"


def finding_to_draft(finding: BountyFinding) -> tuple[str, str, dict]:
    title = f"[Report] {finding.program_name}: {finding.title}"
    body = format_draft_body(finding)
    meta = finding.to_meta()
    return title, body, meta
