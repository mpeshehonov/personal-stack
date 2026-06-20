"""HireHi.ru vacancy list — RF IT job board with public search API."""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import httpx

from job_hunt.config import (
    JOBHUNT_HIREHI_LIMIT,
    JOBHUNT_HIREHI_MAX_PAGES,
    JOBHUNT_USER_AGENT,
    hirehi_subcategories,
)

logger = logging.getLogger(__name__)

HIREHI_API_URL = "https://hirehi.ru/api/search/jobs"
HIREHI_BASE_URL = "https://hirehi.ru"
RATE_LIMIT_SEC = 1.5

_CYRILLIC_TO_LATIN = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
)


def _headers() -> dict[str, str]:
    return {"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}


def slugify_title(title: str) -> str:
    text = title.lower().translate(_CYRILLIC_TO_LATIN)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _parse_rub_salary(text: str) -> int | None:
    match = re.search(r"([\d\s]+)\s*₽", text.replace("\u202f", " "))
    if not match:
        return None
    digits = re.sub(r"\s+", "", match.group(1))
    if not digits.isdigit():
        return None
    return int(digits)


def hirehi_job_url(job: dict[str, Any], url_map: dict[int, str] | None = None) -> str:
    job_id = int(job["id"])
    if url_map and job_id in url_map:
        return url_map[job_id]
    category = job.get("category") or "development"
    slug = slugify_title(job.get("title") or "vacancy")
    return f"{HIREHI_BASE_URL}/{category}/{slug}-{job_id}"


def _fetch_url_map(subcategory: str) -> dict[int, str]:
    """Best-effort id→url map from server-rendered listing HTML."""
    mapping: dict[int, str] = {}
    try:
        resp = httpx.get(
            f"{HIREHI_BASE_URL}/vacancies/{subcategory}",
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return mapping
        for url, job_id in re.findall(
            rf"({re.escape(HIREHI_BASE_URL)}/[a-z]+/[a-z0-9-]+-(\d+))",
            resp.text,
        ):
            mapping[int(job_id)] = url
    except httpx.HTTPError as exc:
        logger.warning("HireHi URL map fetch failed for %s: %s", subcategory, exc)
    return mapping


def hirehi_to_vacancy_shape(job: dict[str, Any], *, url: str) -> dict[str, Any]:
    fmt = job.get("format") or ""
    remote = "удал" in fmt.lower()
    salary_text = job.get("salary_display") or job.get("salary") or ""
    salary_min = _parse_rub_salary(str(salary_text))
    salary = {"from": salary_min, "currency": "RUR"} if salary_min else None
    level = job.get("level") or ""

    return {
        "id": str(job.get("id", "")),
        "name": job.get("title") or "",
        "alternate_url": url,
        "employer": {"name": job.get("company") or ""},
        "key_skills": [],
        "schedule": {"id": "remote" if remote else "fullDay", "name": fmt},
        "salary": salary,
        "snippet": {
            "requirement": f"{level} {salary_text} {fmt}".strip()[:500],
            "responsibility": "",
        },
        "area": {"name": fmt},
        "_source": "hirehi",
    }


def fetch_hirehi_vacancies(
    *,
    subcategory: str,
    max_pages: int | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    max_pages = max_pages if max_pages is not None else JOBHUNT_HIREHI_MAX_PAGES
    limit = limit if limit is not None else JOBHUNT_HIREHI_LIMIT
    url_map = _fetch_url_map(subcategory)

    results: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        if page > 1:
            time.sleep(RATE_LIMIT_SEC)
        try:
            resp = httpx.get(
                HIREHI_API_URL,
                params={
                    "page": page,
                    "limit": limit,
                    "sort": "date",
                    "category": "development",
                    "subcategory": subcategory,
                },
                headers=_headers(),
                timeout=30,
            )
            if resp.status_code != 200:
                logger.warning(
                    "HireHi API returned %s for %s page %s",
                    resp.status_code,
                    subcategory,
                    page,
                )
                break
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.warning("HireHi fetch failed (%s page %s): %s", subcategory, page, exc)
            break

        jobs = data.get("jobs") or []
        if not jobs:
            break
        for job in jobs:
            url = hirehi_job_url(job, url_map)
            results.append(hirehi_to_vacancy_shape(job, url=url))
        if not data.get("has_more"):
            break

    logger.info("HireHi/%s: fetched %s vacancies", subcategory, len(results))
    return results


def fetch_all_hirehi_vacancies() -> list[dict[str, Any]]:
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for subcategory in hirehi_subcategories():
        for item in fetch_hirehi_vacancies(subcategory=subcategory):
            vid = str(item.get("id", ""))
            if not vid or vid in seen:
                continue
            seen.add(vid)
            merged.append(item)
    return merged
