"""FL.ru vacancy tab (kind=5) → HH-like vacancy shapes for job hunt."""

from __future__ import annotations

import html
import logging
import re
import time
from typing import Any

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT

logger = logging.getLogger(__name__)

FL_VACANCIES_URL = "https://www.fl.ru/projects/?kind=5"
RATE_LIMIT_SEC = 0.35

_FE_HINT = re.compile(
    r"react|frontend|front-end|фронт|верст|typescript|next\.?js|javascript|"
    r"html|css|админк|vue|web|сайт|лендинг|разработчик|developer|"
    r"full.?stack|fullstack|node",
    re.I,
)


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
    }


def _strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fl_to_vacancy_shape(
    *,
    external_id: str,
    title: str,
    url: str,
    snippet: str = "",
) -> dict[str, Any]:
    return {
        "id": external_id,
        "name": title,
        "alternate_url": url,
        "employer": {"name": ""},
        "area": {"name": "удалённо"},
        "snippet": {
            "requirement": snippet[:400],
            "responsibility": "",
        },
        "key_skills": [],
        "salary": None,
        "_source": "fl",
        "_actionable": True,
        "_apply_hint_ru": "Отклик прямо на FL.ru",
    }


def fetch_fl_vacancies(*, limit: int = 40) -> list[dict[str, Any]]:
    """Parse FL.ru «Вакансии» tab; keep FE-ish open cards with apply button."""
    try:
        resp = httpx.get(
            FL_VACANCIES_URL,
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            logger.warning("FL vacancies listing HTTP %s", resp.status_code)
            return []
        page = resp.text
    except httpx.HTTPError as exc:
        logger.warning("FL vacancies listing failed: %s", exc)
        return []

    ids = list(dict.fromkeys(re.findall(r"/projects/(\d+)/[^\"']+\.html", page)))
    results: list[dict[str, Any]] = []
    for pid in ids[: max(limit * 2, 50)]:
        i = page.find(f"/projects/{pid}/")
        if i < 0:
            continue
        chunk = page[max(0, i - 900) : i + 1400]
        chunk_text = _strip_html(chunk)
        if not _FE_HINT.search(chunk_text):
            continue
        slug_m = re.search(rf"/projects/{pid}/([^\"']+\.html)", chunk)
        if not slug_m:
            continue
        url = f"https://www.fl.ru/projects/{pid}/{slug_m.group(1)}"
        title_m = re.search(
            rf"/projects/{pid}/[^\"']+\.html\"[^>]*>([^<]{{6,160}})</a>",
            chunk,
        )
        title = ""
        if title_m and title_m.group(1).strip().lower() not in (
            "откликнуться",
            "подробнее",
        ):
            title = html.unescape(title_m.group(1).strip())
        if not title:
            title = slug_m.group(1).replace(".html", "").replace("-", " ")[:120]

        time.sleep(RATE_LIMIT_SEC)
        try:
            det = httpx.get(url, headers=_headers(), timeout=25, follow_redirects=True)
        except httpx.HTTPError:
            continue
        if det.status_code != 200:
            continue
        low = det.text.lower()
        if any(
            x in low
            for x in (
                "проект уже закрыт",
                "похожие проекты на бирже",
                "исполнитель выбран",
                "заказ закрыт",
            )
        ):
            continue
        if "откликнуться" not in low:
            continue
        # Prefer vacancy-tagged pages; still allow if FE title is strong
        is_vac = "ваканси" in low
        if not is_vac and not _FE_HINT.search(title):
            continue
        title_m2 = re.search(r"<title>([^<]+)</title>", det.text, re.I)
        if title_m2:
            t = html.unescape(title_m2.group(1))
            t = re.sub(r":\s*проект в категории.*$", "", t, flags=re.I).strip()
            if t:
                title = t[:160]
        snippet = _strip_html(det.text)[:500]
        results.append(
            fl_to_vacancy_shape(
                external_id=pid,
                title=title,
                url=url,
                snippet=snippet,
            )
        )
        if len(results) >= limit:
            break

    logger.info("FL vacancies: kept %s", len(results))
    return results
