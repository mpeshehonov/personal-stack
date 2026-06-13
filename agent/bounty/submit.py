"""Submit approved bounty reports to external platforms."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from bounty.config import HACKERONE_API_IDENTIFIER, HACKERONE_API_TOKEN
from bounty.models import BountyFinding

logger = logging.getLogger(__name__)

HACKERONE_REPORTS_URL = "https://api.hackerone.com/v1/hackers/reports"
HACKERONE_ME_URL = "https://api.hackerone.com/v1/hackers/me"


@dataclass
class SubmitResult:
    ok: bool
    platform: str
    external_id: str = ""
    report_url: str = ""
    message: str = ""


def hackerone_configured() -> bool:
    return bool(HACKERONE_API_IDENTIFIER and HACKERONE_API_TOKEN)


def verify_hackerone_auth() -> tuple[bool, str]:
    if not hackerone_configured():
        return False, "HackerOne API не настроен"
    try:
        resp = httpx.get(
            HACKERONE_ME_URL,
            auth=(HACKERONE_API_IDENTIFIER, HACKERONE_API_TOKEN),
            headers={"Accept": "application/json"},
            timeout=30,
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
    return SubmitResult(
        ok=False,
        platform=finding.platform,
        message=(
            f"Авто-сабмит для {finding.platform} пока не поддерживается. "
            f"Отчёт готов — отправь вручную: {finding.program_url}"
        ),
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
