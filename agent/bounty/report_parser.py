"""Parse structured bounty findings from agent output."""

from __future__ import annotations

import json
import re
from typing import Any

from bounty.models import BountyFinding
from bounty.programs import BountyProgram

_JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)
_VALID_SEVERITIES = frozenset({"none", "low", "medium", "high", "critical"})


def _normalize_severity(value: str) -> str:
    sev = (value or "medium").strip().lower()
    return sev if sev in _VALID_SEVERITIES else "medium"


def parse_agent_finding(text: str, program: BountyProgram) -> BountyFinding | None:
    """Extract a validated finding from agent markdown/json output."""
    if not text.strip():
        return None

    payload: dict[str, Any] | None = None
    for match in _JSON_BLOCK.finditer(text):
        try:
            candidate = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and "found" in candidate:
            payload = candidate
            break

    if payload is None:
        try:
            candidate = json.loads(text.strip())
            if isinstance(candidate, dict) and "found" in candidate:
                payload = candidate
        except json.JSONDecodeError:
            return None

    if not payload or not payload.get("found"):
        return None

    confidence = str(payload.get("confidence", "")).lower()
    if confidence not in ("high",):
        return None

    title = str(payload.get("title", "")).strip()
    report_md = str(payload.get("report_markdown", "")).strip()
    repro = str(payload.get("reproduction_steps", "")).strip()
    impact = str(payload.get("impact", "")).strip()
    asset = str(payload.get("asset", "")).strip()
    weakness = str(payload.get("weakness_type", "")).strip()

    if not all((title, report_md, repro, impact, asset, weakness)):
        return None
    if len(report_md) < 800 or len(repro) < 120:
        return None

    evidence = payload.get("evidence_commands")
    if isinstance(evidence, list):
        evidence_cmds = [str(x).strip() for x in evidence if str(x).strip()]
    else:
        evidence_cmds = None

    return BountyFinding(
        title=title[:250],
        severity=_normalize_severity(str(payload.get("severity", "medium"))),
        weakness_type=weakness[:120],
        asset=asset[:200],
        report_markdown=report_md,
        reproduction_steps=repro,
        impact=impact,
        program_name=program.name,
        platform=program.platform,
        team_handle=program.team_handle,
        program_url=program.url,
        confidence=confidence,
        evidence_commands=evidence_cmds or None,
    )


def parse_research_lead(text: str, program: BountyProgram) -> dict[str, Any] | None:
    """Extract a research lead when no submit-ready finding."""
    if not text.strip():
        return None

    for match in _JSON_BLOCK.finditer(text):
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue

        best = payload.get("best_candidate")
        if isinstance(best, dict) and best.get("has_finding"):
            title = str(best.get("title", "")).strip()
            asset = str(best.get("asset", "")).strip()
            if title and asset:
                return {
                    "title": title[:200],
                    "severity": str(best.get("severity", "medium")).lower(),
                    "asset": asset[:200],
                    "hypothesis": str(best.get("reproduction_steps") or title)[:500],
                    "weakness_type": str(best.get("weakness_type", ""))[:120],
                    "notes": str(payload.get("notes", ""))[:1500],
                }

        seeds = payload.get("hypothesis_seeds")
        if isinstance(seeds, list) and seeds:
            seed = str(seeds[0]).strip()
            if len(seed) > 20:
                return {
                    "title": seed[:200],
                    "severity": "low",
                    "asset": program.url,
                    "hypothesis": seed,
                    "notes": str(payload.get("notes", ""))[:1500],
                }

    return None


def format_draft_body(finding: BountyFinding) -> str:
    """Human-readable draft stored in SQLite body column."""
    return "\n".join(
        [
            f"Program: {finding.program_name} ({finding.platform})",
            f"URL: {finding.program_url}",
            f"Severity: {finding.severity}",
            f"Weakness: {finding.weakness_type}",
            f"Asset: {finding.asset}",
            "",
            "## Impact",
            finding.impact,
            "",
            "## Steps to reproduce",
            finding.reproduction_steps,
            "",
            "## Full report (submission-ready)",
            finding.report_markdown,
        ]
    )
