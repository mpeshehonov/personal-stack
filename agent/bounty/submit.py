"""Submit approved bounty reports to external platforms."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

from bounty.config import HACKERONE_API_IDENTIFIER, HACKERONE_API_TOKEN
from bounty.models import BountyFinding

logger = logging.getLogger(__name__)

HACKERONE_REPORTS_URL = "https://api.hackerone.com/v1/hackers/reports"
# /hackers/me often returns 401 even with valid creds; me/reports is a reliable auth probe.
HACKERONE_AUTH_CHECK_URL = "https://api.hackerone.com/v1/hackers/me/reports"

EXPORTS_DIR = Path(__file__).resolve().parent / "exports"
IMMUNEFI_DASHBOARD_URL = "https://bugs.immunefi.com/dashboard/new-report"

# Platforms with no public submit API — export markdown for manual paste.
EXPORT_PLATFORMS = frozenset({"immunefi", "hackenproof"})


@dataclass
class SubmitResult:
    ok: bool
    platform: str
    external_id: str = ""
    report_url: str = ""
    message: str = ""
    export_path: str = ""


def hackerone_configured() -> bool:
    return bool(HACKERONE_API_IDENTIFIER and HACKERONE_API_TOKEN)


def platform_supports_api_submit(platform: str) -> bool:
    return platform == "hackerone"


def verify_hackerone_auth() -> tuple[bool, str]:
    if not hackerone_configured():
        return False, "HackerOne API не настроен"
    try:
        resp = httpx.get(
            HACKERONE_AUTH_CHECK_URL,
            auth=(HACKERONE_API_IDENTIFIER, HACKERONE_API_TOKEN),
            headers={"Accept": "application/json"},
            timeout=30,
            params={"page[size]": 1},
        )
    except httpx.HTTPError as e:
        return False, str(e)
    if resp.status_code == 200:
        return True, "OK"
    if resp.status_code == 401:
        return (
            False,
            "401 Unauthorized — проверь HACKERONE_API_IDENTIFIER (не handle?) и токен в secrets/.env.bounty",
        )
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"


def submit_finding(finding: BountyFinding) -> SubmitResult:
    if finding.platform == "hackerone":
        return submit_hackerone(finding)
    if finding.platform in EXPORT_PLATFORMS:
        return export_for_manual_submit(finding)
    return SubmitResult(
        ok=False,
        platform=finding.platform,
        message=(
            f"Авто-сабмит для {finding.platform} пока не поддерживается. "
            f"Отчёт готов — отправь вручную: {finding.program_url}"
        ),
    )


def _slug(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:max_len] or "report"


def _severity_label(severity: str) -> str:
    mapping = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "none": "Informational",
        "informational": "Informational",
    }
    return mapping.get(severity.lower(), severity.title())


def format_export_report(finding: BountyFinding) -> str:
    """Markdown aligned with Immunefi / HackenProof web form fields."""
    lines = [
        f"# {finding.title}",
        "",
        "<!-- Platform export — paste sections into the program submit form -->",
        f"<!-- program: {finding.program_name} | platform: {finding.platform} -->",
        f"<!-- team: {finding.team_handle} | url: {finding.program_url} -->",
        "",
        "## Metadata (form fields)",
        "",
        f"- **Program:** {finding.program_name}",
        f"- **Platform:** {finding.platform}",
        f"- **Team / slug:** {finding.team_handle}",
        f"- **Severity:** {_severity_label(finding.severity)}",
        f"- **Weakness:** {finding.weakness_type}",
        f"- **Asset:** {finding.asset}",
        f"- **Confidence:** {finding.confidence}",
        "",
        "## Description",
        "",
        finding.report_markdown.strip(),
        "",
        "## Steps to Reproduce",
        "",
        finding.reproduction_steps.strip(),
        "",
        "## Impact",
        "",
        finding.impact.strip(),
        "",
        "## Submit",
        "",
    ]
    if finding.platform == "immunefi":
        lines.extend(
            [
                f"1. Open program page: {finding.program_url}",
                f"2. Or dashboard: {IMMUNEFI_DASHBOARD_URL}",
                "3. Paste sections above; verify payout wallet in Immunefi settings.",
            ]
        )
    elif finding.platform == "hackenproof":
        submit_url = finding.program_url.rstrip("/") + "/submit"
        lines.extend(
            [
                f"1. Open: {submit_url}",
                "2. Paste sections above; payout USDC (Base) wallet must be set in profile.",
            ]
        )
    else:
        lines.append(f"Manual submit: {finding.program_url}")
    return "\n".join(lines) + "\n"


def export_report(finding: BountyFinding) -> Path:
    """Write submit-ready markdown to agent/bounty/exports/."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    filename = f"{finding.platform}-{finding.team_handle}-{_slug(finding.title)}-{ts}.md"
    path = EXPORTS_DIR / filename
    path.write_text(format_export_report(finding), encoding="utf-8")
    return path


def export_for_manual_submit(finding: BountyFinding) -> SubmitResult:
    """Export report for platforms without a public submit API."""
    try:
        path = export_report(finding)
    except OSError as e:
        logger.warning("Export failed for %s: %s", finding.platform, e)
        return SubmitResult(
            ok=False,
            platform=finding.platform,
            message=f"Не удалось записать экспорт: {e}",
        )

    export_path = str(path)
    if finding.platform == "immunefi":
        message = (
            f"Immunefi: API-сабмита нет. Экспорт → {export_path}. "
            f"Вставь поля на {finding.program_url} или {IMMUNEFI_DASHBOARD_URL}"
        )
    else:
        submit_url = finding.program_url.rstrip("/") + "/submit"
        message = (
            f"HackenProof: API-сабмита нет. Экспорт → {export_path}. "
            f"Отправь на {submit_url}"
        )

    return SubmitResult(
        ok=False,
        platform=finding.platform,
        report_url=finding.program_url,
        export_path=export_path,
        message=message,
    )


def submit_hackerone(finding: BountyFinding) -> SubmitResult:
    if not hackerone_configured():
        return SubmitResult(
            ok=False,
            platform="hackerone",
            message="HackerOne API не настроен (HACKERONE_API_USERNAME/TOKEN в secrets/.env.bounty)",
        )

    vulnerability_information = finding.report_markdown.strip()
    if finding.reproduction_steps not in vulnerability_information:
        vulnerability_information += (
            "\n\n## Steps to Reproduce\n\n" + finding.reproduction_steps
        )
    if finding.impact not in vulnerability_information:
        vulnerability_information += "\n\n## Impact\n\n" + finding.impact

    payload = {
        "data": {
            "type": "report",
            "attributes": {
                "team_handle": finding.team_handle,
                "title": finding.title,
                "vulnerability_information": vulnerability_information[:50000],
                "impact": finding.impact[:10000],
                "severity_rating": finding.severity,
            },
        }
    }

    try:
        resp = httpx.post(
            HACKERONE_REPORTS_URL,
            json=payload,
            auth=(HACKERONE_API_IDENTIFIER, HACKERONE_API_TOKEN),
            headers={"Accept": "application/json"},
            timeout=60,
        )
    except httpx.HTTPError as e:
        logger.warning("HackerOne submit HTTP error: %s", e)
        return SubmitResult(ok=False, platform="hackerone", message=str(e))

    if resp.status_code not in (200, 201):
        detail = resp.text[:500]
        logger.warning("HackerOne submit failed %s: %s", resp.status_code, detail)
        return SubmitResult(
            ok=False,
            platform="hackerone",
            message=f"HTTP {resp.status_code}: {detail}",
        )

    try:
        data = resp.json()
    except ValueError:
        return SubmitResult(ok=False, platform="hackerone", message="Invalid JSON response")

    attrs = (data.get("data") or {}).get("attributes") or {}
    report_id = str((data.get("data") or {}).get("id") or attrs.get("id") or "")
    report_url = str(attrs.get("url") or "")
    if report_id and not report_url:
        report_url = f"https://hackerone.com/reports/{report_id}"

    return SubmitResult(
        ok=True,
        platform="hackerone",
        external_id=report_id,
        report_url=report_url,
        message="Отчёт отправлен на HackerOne",
    )
