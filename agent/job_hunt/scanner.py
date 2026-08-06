"""Fetch vacancies, score matches, store new leads (read-only — no apply)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from job_hunt.config import (
    JOBHUNT_ENABLED,
    JOBHUNT_HH_AREA,
    JOBHUNT_HH_MAX_PAGES,
    JOBHUNT_HH_PER_PAGE,
    JOBHUNT_HH_TEXT,
    JOBHUNT_MIN_MATCH,
    JOBHUNT_USER_AGENT,
    hh_search_queries,
)
from job_hunt.dedup import dedupe_vacancies, vacancy_fingerprint
from job_hunt.fl_vacancies import fetch_fl_vacancies
from job_hunt.habr import fetch_habr_vacancies
from job_hunt.hirehi import fetch_all_hirehi_vacancies
from job_hunt.hirify import fetch_all_hirify_vacancies
from job_hunt.matcher import load_resume_skills, score_vacancy
from job_hunt.sources import (
    board_enabled,
    enabled_tg_channels,
    ensure_default_sources,
    mark_fetch_success,
    source_key_for_vacancy,
    sources_report_snippet,
)
from job_hunt.telegram_channels import fetch_all_tg_vacancies
from orchestrator.state import add_job_lead, job_lead_exists, job_lead_url_exists

logger = logging.getLogger(__name__)

HH_VACANCIES_URL = "https://api.hh.ru/vacancies"
RATE_LIMIT_SEC = 2.0


def _hh_headers() -> dict[str, str]:
    return {"User-Agent": JOBHUNT_USER_AGENT}


def fetch_hh_vacancies(
    *,
    text: str | None = None,
    area: str | None = None,
    per_page: int | None = None,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch vacancy list from HH.ru public API with rate limiting."""
    text = text if text is not None else JOBHUNT_HH_TEXT
    area = area if area is not None else JOBHUNT_HH_AREA
    per_page = per_page if per_page is not None else JOBHUNT_HH_PER_PAGE
    max_pages = max_pages if max_pages is not None else JOBHUNT_HH_MAX_PAGES

    results: list[dict[str, Any]] = []
    page = 0

    while page < max_pages:
        if page > 0:
            time.sleep(RATE_LIMIT_SEC)
        try:
            resp = httpx.get(
                HH_VACANCIES_URL,
                params={
                    "text": text,
                    "area": area,
                    "schedule": "remote",
                    "per_page": per_page,
                    "page": page,
                },
                headers=_hh_headers(),
                timeout=30,
            )
            if resp.status_code != 200:
                logger.warning("HH.ru API returned %s on page %s", resp.status_code, page)
                break
            data = resp.json()
        except httpx.HTTPError as e:
            logger.warning("HH.ru fetch failed page %s: %s", page, e)
            break

        items = data.get("items") or []
        if not items:
            break
        results.extend(items)

        pages_total = data.get("pages", 0)
        page += 1
        if page >= pages_total:
            break

    return results


def _empty_source_counts() -> dict[str, int]:
    return {
        "hh": 0,
        "habr": 0,
        "hirify": 0,
        "hirehi": 0,
        "fl": 0,
        "telegram": 0,
    }


def fetch_all_vacancies() -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Fetch from enabled weighted sources. Dedup across sources by URL + title/company."""
    ensure_default_sources()
    vacancies: list[dict[str, Any]] = []
    counts = _empty_source_counts()
    seen_hh: set[str] = set()

    if board_enabled("hh"):
        for query in hh_search_queries():
            for item in fetch_hh_vacancies(text=query):
                vid = str(item.get("id", ""))
                if not vid or vid in seen_hh:
                    continue
                seen_hh.add(vid)
                item["_source"] = "hh"
                vacancies.append(item)
        counts["hh"] = len(seen_hh)
        mark_fetch_success("hh", len(seen_hh))

    if board_enabled("habr"):
        habr = fetch_habr_vacancies()
        counts["habr"] = len(habr)
        vacancies.extend(habr)
        mark_fetch_success("habr", len(habr))

    if board_enabled("hirify"):
        hirify = fetch_all_hirify_vacancies()
        counts["hirify"] = len(hirify)
        vacancies.extend(hirify)
        mark_fetch_success("hirify", len(hirify))

    if board_enabled("hirehi"):
        hirehi = fetch_all_hirehi_vacancies()
        counts["hirehi"] = len(hirehi)
        vacancies.extend(hirehi)
        mark_fetch_success("hirehi", len(hirehi))

    if board_enabled("fl"):
        fl = fetch_fl_vacancies()
        counts["fl"] = len(fl)
        vacancies.extend(fl)
        mark_fetch_success("fl", len(fl))

    channels = enabled_tg_channels()
    if channels:
        tg = fetch_all_tg_vacancies(channels=channels)
        counts["telegram"] = len(tg)
        vacancies.extend(tg)
        by_ch: dict[str, int] = {}
        for item in tg:
            key = source_key_for_vacancy(item)
            by_ch[key] = by_ch.get(key, 0) + 1
        for key, n in by_ch.items():
            mark_fetch_success(key, n)

    deduped, skipped = dedupe_vacancies(vacancies)
    if skipped:
        logger.info("Cross-source dedup removed %s duplicate vacancies", skipped)
    return deduped, counts


def _vacancy_to_lead_fields(
    vacancy: dict[str, Any],
    *,
    match_score: int,
    match_reasons: list[str],
) -> dict[str, Any]:
    employer = vacancy.get("employer") or {}
    area = vacancy.get("area") or {}
    skills = [s.get("name") for s in (vacancy.get("key_skills") or []) if s.get("name")]
    snippet_parts = [
        (vacancy.get("snippet") or {}).get("requirement"),
        (vacancy.get("snippet") or {}).get("responsibility"),
    ]
    description_snippet = " ".join(p for p in snippet_parts if p)[:500]

    salary = vacancy.get("salary")
    salary_raw = None
    if salary:
        salary_raw = json.dumps(salary, ensure_ascii=False)

    source = source_key_for_vacancy(vacancy)

    return {
        "source": source,
        "external_id": str(vacancy.get("id", "")),
        "url": vacancy.get("alternate_url") or "",
        "title": vacancy.get("name") or "",
        "company": employer.get("name") or "",
        "salary_raw": salary_raw,
        "location": area.get("name") or "",
        "skills_json": json.dumps(skills, ensure_ascii=False),
        "description_snippet": description_snippet,
        "match_score": match_score,
        "match_reasons_json": json.dumps(match_reasons, ensure_ascii=False),
        "status": "new",
    }


def scan_and_store_leads(
    vacancies: list[dict[str, Any]] | None = None,
    *,
    min_match: int | None = None,
) -> dict[str, Any]:
    """Score vacancies, insert new high-match leads. Returns scan summary."""
    min_match = min_match if min_match is not None else JOBHUNT_MIN_MATCH
    source_counts = _empty_source_counts()
    if vacancies is None:
        vacancies, source_counts = fetch_all_vacancies()

    resume_skills = load_resume_skills()
    new_lead_ids: list[int] = []
    skipped_existing = 0
    skipped_duplicates = 0
    below_threshold = 0
    seen_fingerprints: set[str] = set()

    for vacancy in vacancies:
        source = source_key_for_vacancy(vacancy)
        external_id = str(vacancy.get("id", ""))
        if not external_id:
            continue
        if job_lead_exists(source, external_id):
            skipped_existing += 1
            continue
        # Legacy rows may use source=telegram
        if source.startswith("tg:") and job_lead_exists("telegram", external_id):
            skipped_existing += 1
            continue

        url = vacancy.get("alternate_url") or ""
        if url and job_lead_url_exists(url):
            skipped_duplicates += 1
            continue

        fp = vacancy_fingerprint(vacancy)
        if fp and len(fp) >= 8 and fp in seen_fingerprints:
            skipped_duplicates += 1
            continue

        score, reasons = score_vacancy(vacancy, resume_skills=resume_skills)
        if score < min_match:
            below_threshold += 1
            continue

        fields = _vacancy_to_lead_fields(vacancy, match_score=score, match_reasons=reasons)
        lead_id = add_job_lead(**fields)
        try:
            from opportunity.services import upsert_from_job_lead

            upsert_from_job_lead(
                lead_id=lead_id,
                vacancy=vacancy,
                match_score=score,
                match_reasons=reasons,
                lead_status="new",
            )
        except Exception:
            logger.exception("Opportunity upsert failed for lead %s", lead_id)
        new_lead_ids.append(lead_id)
        if fp and len(fp) >= 8:
            seen_fingerprints.add(fp)

    top_leads = list_job_leads_for_summary(new_lead_ids)
    return {
        "enabled": True,
        "fetched": len(vacancies),
        "by_source": source_counts,
        "new_count": len(new_lead_ids),
        "skipped_existing": skipped_existing,
        "skipped_duplicates": skipped_duplicates,
        "below_threshold": below_threshold,
        "top_leads": top_leads,
        "sources_snippet": sources_report_snippet(),
    }


def list_job_leads_for_summary(new_ids: list[int]) -> list[dict[str, Any]]:
    """Build top-5 summary from freshly inserted IDs (fallback: query DB)."""
    from orchestrator.state import get_job_lead, list_job_leads

    leads: list[dict[str, Any]] = []
    for lead_id in new_ids:
        row = get_job_lead(lead_id)
        if row:
            leads.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "company": row["company"],
                    "score": row["match_score"],
                    "url": row["url"],
                    "source": row["source"],
                }
            )
    leads.sort(key=lambda x: x["score"], reverse=True)
    if len(leads) >= 5:
        return leads[:5]

    for row in list_job_leads(status="new", limit=5, min_score=JOBHUNT_MIN_MATCH):
        if any(x["id"] == row["id"] for x in leads):
            continue
        leads.append(
            {
                "id": row["id"],
                "title": row["title"],
                "company": row["company"],
                "score": row["match_score"],
                "url": row["url"],
                "source": row["source"],
            }
        )
        if len(leads) >= 5:
            break
    return leads[:5]


def daily_job_scan() -> dict[str, Any]:
    """Daily scan hook for orchestrator. Read-only — no applications submitted."""
    if not JOBHUNT_ENABLED:
        logger.info("Job hunt disabled (JOBHUNT_ENABLED=false)")
        return {
            "enabled": False,
            "new_count": 0,
            "top_leads": [],
            "fetched": 0,
        }

    try:
        summary = scan_and_store_leads()
        try:
            from opportunity.services import after_scan_hook

            summary = after_scan_hook(summary)
        except Exception:
            logger.exception("Opportunity after_scan_hook failed")
        logger.info(
            "Job hunt scan: fetched=%s new=%s skipped=%s below=%s",
            summary["fetched"],
            summary["new_count"],
            summary["skipped_existing"],
            summary["below_threshold"],
        )
        return summary
    except Exception as e:
        logger.exception("Job hunt scan failed")
        return {
            "enabled": True,
            "error": str(e),
            "new_count": 0,
            "top_leads": [],
            "fetched": 0,
        }
