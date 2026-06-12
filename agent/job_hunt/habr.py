"""Habr Career vacancy list (HTML) — fallback when HH.ru API is blocked."""

from __future__ import annotations

import html
import logging
import re
from typing import Any

import httpx

from job_hunt.config import JOBHUNT_HABR_QUERY, JOBHUNT_USER_AGENT

logger = logging.getLogger(__name__)

HABR_SEARCH_URL = "https://career.habr.com/vacancies"

_CARD_SPLIT = re.compile(r'class="vacancy-card vacancy-card--bp"')
_TITLE_RE = re.compile(
    r'aria-label="(?P<title>[^"]+)".*?href="/vacancies/(?P<id>\d+)"',
    re.DOTALL,
)
_COMPANY_RE = re.compile(
    r'class="link-comp link-comp--appearance-dark" href="/companies/[^"]+">(?P<company>[^<]+)</a>'
)
_SALARY_RE = re.compile(
    r'predicted-salary__title[^>]*>(?P<salary>[^<]+)</h4>'
)


def _habr_headers() -> dict[str, str]:
    return {"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}


def fetch_habr_vacancies(*, query: str | None = None) -> list[dict[str, Any]]:
    """Fetch vacancy cards from Habr Career search (works from NL VPS)."""
    query = query if query is not None else JOBHUNT_HABR_QUERY
    try:
        resp = httpx.get(
            HABR_SEARCH_URL,
            params={"q": query, "type": "all", "sort": "date"},
            headers=_habr_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            logger.warning("Habr Career returned %s", resp.status_code)
            return []
        page = resp.text
    except httpx.HTTPError as e:
        logger.warning("Habr Career fetch failed: %s", e)
        return []

    chunks = _CARD_SPLIT.split(page)[1:]
    results: list[dict[str, Any]] = []
    for chunk in chunks:
        title_m = _TITLE_RE.search(chunk)
        if not title_m:
            continue
        company_m = _COMPANY_RE.search(chunk)
        salary_m = _SALARY_RE.search(chunk)
        vid = title_m.group("id")
        title = html.unescape(title_m.group("title").strip())
        company = html.unescape(company_m.group("company").strip()) if company_m else ""
        salary_text = salary_m.group("salary").strip() if salary_m else ""
        results.append(habr_to_vacancy_shape(vid, title, company, salary_text))

    logger.info("Habr Career: parsed %s vacancies", len(results))
    return results


def habr_to_vacancy_shape(
    external_id: str,
    title: str,
    company: str,
    salary_text: str = "",
) -> dict[str, Any]:
    """Normalize Habr card to HH-like dict for matcher + lead storage."""
    desc = salary_text
    remote = "удал" in title.lower() or "remote" in title.lower()
    return {
        "id": external_id,
        "name": title,
        "alternate_url": f"https://career.habr.com/vacancies/{external_id}",
        "employer": {"name": company},
        "key_skills": [],
        "schedule": {"id": "remote" if remote else "fullDay", "name": "удалённо" if remote else ""},
        "salary": None,
        "snippet": {"requirement": desc, "responsibility": ""},
        "area": {"name": ""},
        "_source": "habr",
    }
