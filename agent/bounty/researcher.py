"""Run multi-stage bounty research for one program."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from bounty.config import (
    BOUNTY_RESEARCH_PHASES,
    BOUNTY_REVIEW_ENABLED,
    BOUNTY_SAVE_LEADS,
    BOUNTY_SHOPIFY_FOCUS,
)
from bounty.models import BountyFinding
from bounty.programs import BountyProgram
from bounty.report_parser import format_draft_body, parse_agent_finding, parse_research_lead
from bounty.reviewer import review_finding
from bounty.validator import validate_finding
from orchestrator.config import STACK_DIR, TASKS_DIR
from orchestrator.cursor_runner import run_bounty_agent_prompt
from orchestrator.cursor_session import CursorBusyError
from orchestrator.state import add_bounty_draft

logger = logging.getLogger(__name__)

RESEARCH_CACHE = STACK_DIR / "agent" / "bounty" / "research_cache"

_PHASES: tuple[tuple[str, str], ...] = (
    ("scope", "bounty_scope_prompt.md"),
    ("recon", "bounty_recon_prompt.md"),
    ("hunt", "bounty_hunt_prompt.md"),
    ("report", "bounty_research_prompt.md"),
)

_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)


def _load_prompt_template(name: str) -> str:
    return (TASKS_DIR / name).read_text(encoding="utf-8")


def _program_slug(program: BountyProgram) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", program.team_handle.lower()).strip("-") or "program"


def _cache_dir(program: BountyProgram) -> Path:
    d = RESEARCH_CACHE / _program_slug(program)
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_phase_prompt(
    template_name: str,
    program: BountyProgram,
    *,
    prior_context: str = "",
) -> str:
    template = _load_prompt_template(template_name)
    fmt: dict[str, str] = {
        "program_name": program.name,
        "platform": program.platform,
        "program_url": program.url,
        "team_handle": program.team_handle,
        "program_focus": program.focus,
        "program_notes": program.notes or "—",
        "prior_context": prior_context or "— (первая фаза)",
    }
    if "{shopify_playbook}" in template:
        playbook = ""
        if program.team_handle == "shopify":
            path = TASKS_DIR / "bounty_shopify_playbook.md"
            if path.exists():
                playbook = path.read_text(encoding="utf-8")
        fmt["shopify_playbook"] = playbook or "—"
    return template.format(**fmt)


def _extract_json_blocks(text: str) -> list[dict]:
    blocks: list[dict] = []
    for match in _JSON_BLOCK.finditer(text):
        try:
            obj = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            blocks.append(obj)
    return blocks


def _run_phases(program: BountyProgram) -> tuple[str, list[str]]:
    """Run scope → recon → hunt → report. Returns (final_raw, phase_log)."""
    cache = _cache_dir(program)
    context_parts: list[str] = []
    phase_log: list[str] = []
    final_raw = ""

    phases = _PHASES if BOUNTY_RESEARCH_PHASES else (_PHASES[-1],)
    reset = True

    for phase_name, template in phases:
        prior = "\n\n---\n\n".join(context_parts[-3:])
        prompt = build_phase_prompt(template, program, prior_context=prior)
        logger.info("Bounty phase %s: %s (%s)", phase_name, program.name, program.platform)

        raw = run_bounty_agent_prompt(prompt, phase=phase_name, reset=reset)
        reset = False

        if raw.startswith("Cursor ") or "CURSOR_API_KEY" in raw:
            raise RuntimeError(raw[:300])

        (cache / f"{phase_name}.md").write_text(raw, encoding="utf-8")
        summary = raw[:3500]
        context_parts.append(f"## Phase {phase_name}\n{summary}")
        phase_log.append(f"{phase_name}: {len(raw)} chars")
        final_raw = raw

    return final_raw, phase_log


def _save_lead_draft(program: BountyProgram, raw: str, phase_log: list[str]) -> int | None:
    if not BOUNTY_SAVE_LEADS:
        return None
    lead = parse_research_lead(raw, program)
    if not lead:
        return None

    title = f"[Lead] {program.name}: {lead['title'][:100]}"
    body = "\n".join(
        [
            f"Program: {program.name} ({program.platform})",
            f"URL: {program.url}",
            f"Severity (estimated): {lead.get('severity', 'unknown')}",
            f"Asset: {lead.get('asset', '—')}",
            "",
            "## Hypothesis",
            lead.get("hypothesis", lead.get("title", "")),
            "",
            "## Research phases",
            ", ".join(phase_log),
            "",
            "## Notes",
            lead.get("notes", raw[-2000:]),
        ]
    )
    meta = {
        "kind": "lead",
        "program_name": program.name,
        "platform": program.platform,
        "team_handle": program.team_handle,
        "program_url": program.url,
        **{k: v for k, v in lead.items() if k not in ("kind",)},
    }
    return add_bounty_draft(title, body, meta)


def research_program(program: BountyProgram) -> tuple[BountyFinding | None, str]:
    """Multi-phase research → validate → review. Returns (finding, log)."""
    try:
        raw, phase_log = _run_phases(program)
    except CursorBusyError as e:
        raise
    except Exception as e:
        return None, f"{program.name}: ошибка фаз — {e}"

    phases_summary = " → ".join(phase_log)
    research_summary = raw[:2500]

    finding = parse_agent_finding(raw, program)
    if not finding:
        lead_id = _save_lead_draft(program, raw, phase_log)
        if lead_id:
            return None, (
                f"{program.name}: submit-ready нет, сохранён lead #{lead_id} "
                f"({phases_summary})"
            )
        return None, f"{program.name}: submit-ready нет ({phases_summary})"

    ok, reasons = validate_finding(finding)
    if not ok:
        logger.info("Bounty auto-reject %s: %s", program.name, reasons)
        lead_id = _save_lead_draft(program, raw, phase_log)
        suffix = f", lead #{lead_id}" if lead_id else ""
        return None, (
            f"{program.name}: auto-reject — {'; '.join(reasons[:4])}{suffix} "
            f"({phases_summary})"
        )

    if BOUNTY_REVIEW_ENABLED:
        approved, score, review_reasons = review_finding(
            finding,
            program,
            research_summary=research_summary,
        )
        finding.quality_score = score
        if not approved:
            logger.info("Bounty review reject %s: %s", program.name, review_reasons)
            lead_id = _save_lead_draft(program, raw, phase_log)
            suffix = f", lead #{lead_id}" if lead_id else ""
            return None, (
                f"{program.name}: review reject (score {score}) — "
                f"{'; '.join(review_reasons[:4])}{suffix} ({phases_summary})"
            )
        logger.info("Bounty finding approved: %s (score %s)", finding.title[:60], score)

    return finding, f"{program.name}: submit-ready — {finding.title[:80]} ({phases_summary})"


def finding_to_draft(finding: BountyFinding) -> tuple[str, str, dict]:
    title = f"[Report] {finding.program_name}: {finding.title}"
    body = format_draft_body(finding)
    meta = finding.to_meta()
    meta["kind"] = "report"
    return title, body, meta
