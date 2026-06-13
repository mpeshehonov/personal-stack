"""Automated quality gates for submit-ready bounty reports."""

from __future__ import annotations

import re

from bounty.models import BountyFinding

_GHSA = re.compile(r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}", re.I)
_CVE_ONLY = re.compile(r"^CVE-\d{4}-\d+", re.I)
_NUMBERED_STEP = re.compile(r"(?m)^\s*\d+[\).\]]\s+\S")
_VAGUE = re.compile(
    r"\b(might be|could potentially|possibly vulnerable|needs?( further)? (testing|investigation)|"
    r"theoretically|appears to be|suspected|unverified)\b",
    re.I,
)
_REQUIRED_SECTIONS = (
    ("summary", re.compile(r"(?i)\b(summary|executive summary)\b")),
    ("impact", re.compile(r"(?i)\b(impact|security impact)\b")),
    ("steps", re.compile(r"(?i)(steps to reproduce|reproduction|proof of concept|poc)")),
    ("remediation", re.compile(r"(?i)\b(remediation|recommendation|fix)\b")),
)
_HTTP = re.compile(r"^https?://", re.I)
_CURL_OR_CMD = re.compile(r"(?m)(curl |httpie |fetch\(|```(?:bash|sh|http)|GET /|POST /)")


def validate_finding(finding: BountyFinding) -> tuple[bool, list[str]]:
    """Return (ok, rejection_reasons)."""
    reasons: list[str] = []

    if finding.confidence != "high":
        reasons.append("confidence != high")

    if len(finding.title) < 12:
        reasons.append("title слишком короткий")

    if not _HTTP.match(finding.asset):
        reasons.append("asset должен быть полным http(s) URL in-scope")

    if len(finding.impact) < 80:
        reasons.append("impact < 80 символов")

    if len(finding.reproduction_steps) < 120:
        reasons.append("reproduction_steps < 120 символов")

    steps = _NUMBERED_STEP.findall(finding.reproduction_steps)
    if len(steps) < 3:
        reasons.append("нужно ≥3 нумерованных шага воспроизведения")

    if len(finding.report_markdown) < 800:
        reasons.append("report_markdown < 800 символов")

    combined = "\n".join(
        (finding.title, finding.report_markdown, finding.reproduction_steps, finding.impact)
    )
    combined_lower = combined.lower()

    if _GHSA.search(combined) and not _CURL_OR_CMD.search(combined):
        reasons.append("похоже на GHSA/CVE advisory без собственного PoC")

    if _CVE_ONLY.match(finding.title.strip()):
        reasons.append("title выглядит как CVE duplicate")

    if _VAGUE.search(combined):
        reasons.append("формулировки без подтверждённого PoC (might/could/suspected)")

    for name, pattern in _REQUIRED_SECTIONS:
        if not pattern.search(combined_lower):
            if name == "steps" and _NUMBERED_STEP.search(finding.reproduction_steps):
                continue
            reasons.append(f"нет секции {name} в отчёте")

    if not _CURL_OR_CMD.search(combined):
        reasons.append("нет команд/curl/PoC-доказательства в тексте")

    weakness = finding.weakness_type.strip().lower()
    if not weakness or weakness in ("unknown", "other", "n/a"):
        reasons.append("weakness_type не указан")

    return (len(reasons) == 0, reasons)
