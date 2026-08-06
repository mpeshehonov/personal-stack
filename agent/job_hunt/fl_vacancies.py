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
    r"(?:react|frontend|front[- ]?end|фронт(?:енд)?|верстк\w*|typescript|"
    r"next\.?js|javascript|\bjs\b|админк\w*|vue(?:\.js)?|\bnuxt\b|"
    r"лендинг\w*|сайт\w*|web[- ]?design|веб[- ]?дизайн|разработчик|"
    r"developer|full[- ]?stack|fullstack|\bnode(?:\.?js)?\b|\bcss\b|"
    r"(?<!\.)\bhtml\b(?!\.))",
    re.I,
)

_FE_STRONG = re.compile(
    r"react|frontend|front[- ]?end|фронт(?:енд)?|верстк|typescript|next\.?js|"
    r"javascript|vue|nuxt|лендинг|fullstack|full[- ]?stack|web[- ]?design|"
    r"веб[- ]?дизайн|разработчик сайт|сайт на",
    re.I,
)

_NON_FE_CATEGORY = re.compile(
    r"аудио|звук|монтаж|видеооператор|копирайт|перевод|юрист|бухгалтер|"
    r"менеджер|продажи|smm|таргет|seo(?!\s*site)|1[cс]|битрикс24|"
    r"мобильн|android|ios|swift|kotlin|unity|unreal",
    re.I,
)


def _looks_fe(text: str) -> bool:
    return bool(_FE_HINT.search(text or ""))


def _looks_strong_fe(text: str) -> bool:
    return bool(_FE_STRONG.search(text or ""))


def _slug_text(slug: str) -> str:
    return slug.replace(".html", "").replace("-", " ").replace("_", " ")


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
    for pid in ids[: max(limit * 3, 60)]:
        i = page.find(f"/projects/{pid}/")
        if i < 0:
            continue
        chunk = page[max(0, i - 900) : i + 1400]
        slug_m = re.search(rf"/projects/{pid}/([^\"']+\.html)", chunk)
        if not slug_m:
            continue
        slug = slug_m.group(1)
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
            title = _slug_text(slug)[:120]

        listing_blob = f"{title} {_slug_text(slug)}"
        if _NON_FE_CATEGORY.search(listing_blob) and not _looks_strong_fe(listing_blob):
            continue
        if not _looks_fe(listing_blob):
            continue

        url = f"https://www.fl.ru/projects/{pid}/{slug}"
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

        title_m2 = re.search(r"<title>([^<]+)</title>", det.text, re.I)
        if title_m2:
            t = html.unescape(title_m2.group(1))
            t = re.sub(r":\s*проект в категории.*$", "", t, flags=re.I).strip()
            if t:
                title = t[:160]

        category_m = re.search(
            r"категори[яи]\s+([^,<]{3,80})",
            det.text,
            re.I,
        )
        category = html.unescape(category_m.group(1)).strip() if category_m else ""
        snippet = _strip_html(det.text)[:800]
        blob = f"{title} {category} {snippet[:400]}"
        if _NON_FE_CATEGORY.search(f"{title} {category}") and not _looks_strong_fe(blob):
            continue
        if not (_looks_strong_fe(blob) or _looks_fe(f"{title} {category}")):
            continue

        results.append(
            fl_to_vacancy_shape(
                external_id=pid,
                title=title,
                url=url,
                snippet=snippet[:500],
            )
        )
        if len(results) >= limit:
            break

    logger.info("FL vacancies: kept %s", len(results))
    return results
