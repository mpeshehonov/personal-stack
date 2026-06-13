"""Run Cursor agent bounty research for one program."""

from __future__ import annotations

import logging

from bounty.models import BountyFinding
from bounty.programs import BountyProgram
from bounty.report_parser import format_draft_body, parse_agent_finding
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


def research_program(program: BountyProgram) -> BountyFinding | None:
    """One-shot agent run; returns finding or None."""
    prompt = build_research_prompt(program)
    logger.info("Bounty research start: %s (%s)", program.name, program.platform)
    raw = run_cursor_prompt(prompt, one_shot=True)
    finding = parse_agent_finding(raw, program)
    if finding:
        logger.info("Bounty finding validated: %s", finding.title[:80])
    else:
        logger.info("Bounty research: no submit-ready finding for %s", program.name)
    return finding


def finding_to_draft(finding: BountyFinding) -> tuple[str, str, dict]:
    title = f"[Report] {finding.program_name}: {finding.title}"
    body = format_draft_body(finding)
    return title, body, finding.to_meta()
