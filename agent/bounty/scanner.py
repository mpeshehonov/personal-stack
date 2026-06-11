"""Bug bounty research feeds and draft management."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from bounty.programs import WEB_JS_PROGRAMS, program_by_index
from orchestrator.state import (
    add_bounty_draft,
    bounty_draft_ghsa_ids,
    get_last_program_suggestion,
    set_last_program_suggestion,
)

logger = logging.getLogger(__name__)

GITHUB_ADVISORIES_URL = "https://api.github.com/advisories"
DISCLOSE_PROGRAM_LIST_URL = (
    "https://raw.githubusercontent.com/disclose/diodb/master/program-list.json"
)
SEVERITY_FILTER = frozenset({"high", "critical"})
WEB_ECOSYSTEMS = ("npm", "composer", "rubygems")
PROGRAM_SUGGESTION_COOLDOWN_DAYS = 7


def fetch_disclose_programs(limit: int = 20) -> list[dict[str, Any]]:
    """Fetch public VDP/BBP directory from disclose.io (diodb)."""
    try:
        resp = httpx.get(DISCLOSE_PROGRAM_LIST_URL, timeout=30)
        if resp.status_code != 200:
            return []
        programs = resp.json()
        bounty = [
            p
            for p in programs
            if str(p.get("offers_bounty", "")).lower() in ("yes", "true")
            and p.get("policy_url_status") == "alive"
        ]
        return bounty[:limit]
    except (httpx.HTTPError, ValueError) as e:
        logger.warning("Disclose.io program list fetch failed: %s", e)
        return []


def fetch_github_advisories(
    limit: int = 10,
    *,
    severities: tuple[str, ...] = ("high", "critical"),
    ecosystems: tuple[str, ...] = WEB_ECOSYSTEMS,
) -> list[dict[str, Any]]:
    """Fetch recent GitHub security advisories filtered by severity and ecosystem."""
    seen_ghsa: set[str] = set()
    results: list[dict[str, Any]] = []

    for severity in severities:
        if severity not in SEVERITY_FILTER:
            continue
        for ecosystem in ecosystems:
            if len(results) >= limit:
                break
            try:
                resp = httpx.get(
                    GITHUB_ADVISORIES_URL,
                    params={
                        "per_page": min(limit, 30),
                        "severity": severity,
                        "ecosystem": ecosystem,
                    },
                    headers={"Accept": "application/vnd.github+json"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    continue
                for adv in resp.json():
                    ghsa = adv.get("ghsa_id")
                    if not ghsa or ghsa in seen_ghsa:
                        continue
                    if adv.get("severity", "").lower() not in SEVERITY_FILTER:
                        continue
                    seen_ghsa.add(ghsa)
                    results.append(adv)
                    if len(results) >= limit:
                        break
            except httpx.HTTPError as e:
                logger.warning(
                    "GitHub advisories fetch failed (%s/%s): %s",
                    severity,
                    ecosystem,
                    e,
                )

    results.sort(
        key=lambda a: a.get("published_at") or "",
        reverse=True,
    )
    return results[:limit]


def _extract_cve_ids(adv: dict[str, Any]) -> list[str]:
    cves: list[str] = []
    if cve := adv.get("cve_id"):
        cves.append(cve)
    for ident in adv.get("identifiers") or []:
        if ident.get("type") == "CVE" and ident.get("value"):
            val = ident["value"]
            if val not in cves:
                cves.append(val)
    return cves


def _extract_affected_packages(adv: dict[str, Any]) -> list[str]:
    packages: list[str] = []
    for vuln in adv.get("vulnerabilities") or []:
        pkg = vuln.get("package") or {}
        ecosystem = pkg.get("ecosystem", "")
        name = pkg.get("name", "")
        if not name:
            continue
        label = f"{ecosystem}:{name}" if ecosystem else name
        if label not in packages:
            packages.append(label)
    return packages


def _format_advisory_draft(adv: dict[str, Any]) -> tuple[str, str]:
    ghsa = adv.get("ghsa_id", "unknown")
    cves = _extract_cve_ids(adv)
    packages = _extract_affected_packages(adv)
    summary = (adv.get("summary") or "")[:120]

    title = f"[Draft] Review GHSA {ghsa}: {summary}"
    body_lines = [
        f"Source: GitHub Advisory {ghsa}",
        f"Severity: {adv.get('severity', 'unknown')}",
        f"CVE IDs: {', '.join(cves) if cves else 'none listed'}",
        f"Affected packages: {', '.join(packages) if packages else 'none listed'}",
        f"Summary: {adv.get('summary', '')}",
        "",
        f"URL: {adv.get('html_url', '')}",
        "",
        "Status: DRAFT — requires /approve bounty <id> before any submission.",
        "Use /bounty to list pending drafts.",
    ]
    return title, "\n".join(body_lines)


def _format_program_suggestion_draft(
    program_index: int,
    disclose_count: int,
) -> tuple[str, str]:
    program = program_by_index(program_index)
    title = f"[Program] Explore {program.name} ({program.platform})"
    body_lines = [
        f"Suggested program: {program.name}",
        f"Platform: {program.platform}",
        f"URL: {program.url}",
        f"Focus: {program.focus}",
        f"Notes: {program.notes}",
        "",
        f"Disclose.io directory: {disclose_count} active bounty programs fetched.",
        f"Directory: {DISCLOSE_PROGRAM_LIST_URL}",
        "",
        "Next steps:",
        "1. Read full scope and out-of-scope rules on the program page.",
        "2. Set up a test account/environment if required.",
        "3. Hunt for web/API issues aligned with your JS stack skills.",
        "",
        "Status: SUGGESTION — no submission until you find a valid finding.",
    ]
    return title, "\n".join(body_lines)


def _should_suggest_program() -> bool:
    last = get_last_program_suggestion()
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return True
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(days=PROGRAM_SUGGESTION_COOLDOWN_DAYS)
    return last_dt < cutoff


def daily_bounty_scan() -> list[int]:
    """Scan sources and create draft reports for Telegram approval."""
    draft_ids: list[int] = []
    existing_ghsa = bounty_draft_ghsa_ids()

    disclose_programs = fetch_disclose_programs(limit=50)
    advisories = fetch_github_advisories(8)

    for adv in advisories:
        ghsa = adv.get("ghsa_id")
        if not ghsa or ghsa in existing_ghsa:
            continue
        title, body = _format_advisory_draft(adv)
        draft_id = add_bounty_draft(title, body)
        draft_ids.append(draft_id)
        existing_ghsa.add(ghsa)

    if _should_suggest_program():
        day_index = datetime.now(timezone.utc).timetuple().tm_yday % len(WEB_JS_PROGRAMS)
        title, body = _format_program_suggestion_draft(
            day_index,
            len(disclose_programs),
        )
        draft_id = add_bounty_draft(title, body)
        draft_ids.append(draft_id)
        set_last_program_suggestion()

    return draft_ids
