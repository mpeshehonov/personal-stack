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
    if len(report_md) < 200 or len(repro) < 80:
        return None

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
    )


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
