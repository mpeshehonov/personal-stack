"""Hirify.me vacancy list — aggregates RF IT jobs from Telegram + career sites."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from job_hunt.config import (
    JOBHUNT_HIRIFY_MAX_PAGES,
    JOBHUNT_HIRIFY_QUERY,
    JOBHUNT_USER_AGENT,
    hirify_search_queries,
)

logger = logging.getLogger(__name__)

HIRIFY_API_URL = "https://api.hirify.me/api/vacancies"
RATE_LIMIT_SEC = 1.5


def _headers() -> dict[str, str]:
    return {"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}


def _salary_to_hh(salary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not salary:
        return None
    currency = (salary.get("currency") or "").upper()
    if currency not in ("RUB", "RUR"):
        return None
    amount = salary.get("min")
    if amount is None:
        return None
    result: dict[str, Any] = {"from": int(amount), "currency": "RUR"}
    if salary.get("max") is not None:
        result["to"] = int(salary["max"])
    return result


def hirify_to_vacancy_shape(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize Hirify API item to HH-like dict for matcher + lead storage."""
    tags = [t.get("name") for t in (item.get("tags") or []) if t.get("name")]
    work_format = item.get("work_format") or []
    remote = any(fmt == "remote" for fmt in work_format)
    company = (item.get("company_title") or "").strip()
    if company == "%hirify_global%":
        company = ""

    regions = [r.get("name") for r in (item.get("regions") or []) if r.get("name")]
    slug = item.get("slug") or str(item.get("id", ""))
    published = item.get("published_at") or item.get("created_at") or item.get("date")

    # Public Hirify cards usually hide contacts behind Plus → low actionability
    has_external = bool(item.get("source_url") or item.get("external_url") or item.get("apply_url"))
    company_ok = bool(company)

    return {
        "id": str(item.get("id", "")),
        "name": item.get("title") or "",
        "alternate_url": f"https://hirify.me/jobs/{slug}",
        "employer": {"name": company},
        "key_skills": [{"name": t} for t in tags],
        "schedule": {
            "id": "remote" if remote else "fullDay",
            "name": "удалённо" if remote else "",
        },
        "salary": _salary_to_hh(item.get("salary")),
        "snippet": {
            "requirement": " ".join(tags)[:500],
            "responsibility": (item.get("tldr") or "")[:500],
        },
        "area": {"name": ", ".join(regions)},
        "published_at": published,
        "_source": "hirify",
        "_published_at": published,
        "_paywall": not has_external,
        "_actionable": bool(has_external and company_ok),
    }


def fetch_hirify_vacancies(
    *,
    query: str | None = None,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch vacancies from Hirify public API."""
    query = query if query is not None else JOBHUNT_HIRIFY_QUERY
    max_pages = max_pages if max_pages is not None else JOBHUNT_HIRIFY_MAX_PAGES

    results: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        if page > 1:
            time.sleep(RATE_LIMIT_SEC)
        try:
            resp = httpx.get(
                HIRIFY_API_URL,
                params={"page": page, "search": query},
                headers=_headers(),
                timeout=30,
            )
            if resp.status_code != 200:
                logger.warning("Hirify API returned %s on page %s", resp.status_code, page)
                break
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.warning("Hirify fetch failed page %s: %s", page, exc)
            break

        items = data.get("data") or []
        if not items:
            break
        for item in items:
            if item.get("is_archived"):
                continue
            results.append(hirify_to_vacancy_shape(item))

        if page >= data.get("last_page", page):
            break

    logger.info("Hirify: fetched %s vacancies (query=%r)", len(results), query)
    return results


def fetch_all_hirify_vacancies() -> list[dict[str, Any]]:
    """Run configured Hirify queries with in-source dedup by id."""
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for query in hirify_search_queries():
        for item in fetch_hirify_vacancies(query=query):
            vid = str(item.get("id", ""))
            if not vid or vid in seen:
                continue
            seen.add(vid)
            merged.append(item)
    return merged
