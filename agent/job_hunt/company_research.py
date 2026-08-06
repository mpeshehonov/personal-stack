"""Find a direct apply path for a company (HH / career search) — skip aggregator bots."""

from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import quote_plus

import httpx

from job_hunt.apply_path import is_aggregator_url, is_direct_career_url
from job_hunt.config import JOBHUNT_USER_AGENT

logger = logging.getLogger(__name__)

HH_EMPLOYERS_URL = "https://api.hh.ru/employers"
HH_VACANCIES_URL = "https://api.hh.ru/vacancies"
RATE_LIMIT_SEC = 0.8

_FE_QUERY = "frontend OR react OR typescript OR «фронтенд» OR «frontend»"


def _headers() -> dict[str, str]:
    return {"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"}


def hh_search_url(company: str, *, title: str = "") -> str:
    q = " ".join(p for p in (company, "frontend", title.split()[0] if title else "") if p).strip()
    return f"https://hh.ru/search/vacancy?text={quote_plus(q)}&schedule=remote"


def career_web_search_url(company: str) -> str:
    """Google query aimed at company career landings (tilda/career pages, etc.)."""
    q = f'{company} (карьера OR careers OR jobs OR "присоединяйся" OR vacancy OR вакансии)'
    return f"https://www.google.com/search?q={quote_plus(q)}"


def linkedin_people_search_url(company: str) -> str:
    q = f"{company} recruiter OR HR OR «рекрутер» OR «HR»"
    return f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(q)}"


def telegram_web_search_url(company: str) -> str:
    """Best-effort: public web search for HR telegram near company name."""
    q = f'{company} (telegram OR t.me OR "@") (HR OR рекрутер OR вакансия OR hiring)'
    return f"https://www.google.com/search?q={quote_plus(q)}"


def title_web_search_url(title: str) -> str:
    title = (title or "").strip()
    if len(title) < 6:
        return ""
    q = f'"{title}" (вакансия OR careers OR "hh.ru" OR карьера OR отклик)'
    return f"https://www.google.com/search?q={quote_plus(q)}"


def build_research_links(company: str, *, title: str = "") -> dict[str, str]:
    company = (company or "").strip()
    out: dict[str, str] = {}
    if company and company not in ("—", "-", "название компании из текста"):
        out = {
            "hh_search_url": hh_search_url(company, title=title),
            "career_search_url": career_web_search_url(company),
            "linkedin_search_url": linkedin_people_search_url(company),
            "tg_hr_search_url": telegram_web_search_url(company),
        }
    title_url = title_web_search_url(title)
    if title_url and "career_search_url" not in out:
        out["career_search_url"] = title_url
    elif title_url:
        out["title_search_url"] = title_url
    return out


def _norm_name(name: str) -> str:
    return re.sub(r"[\s«»\"'.,]+", " ", (name or "").lower()).strip()


def search_hh_employer(company: str) -> dict[str, Any] | None:
    company = (company or "").strip()
    if len(company) < 2:
        return None
    try:
        resp = httpx.get(
            HH_EMPLOYERS_URL,
            params={"text": company, "per_page": 10},
            headers=_headers(),
            timeout=20,
        )
        if resp.status_code != 200:
            return None
        items = resp.json().get("items") or []
    except httpx.HTTPError as exc:
        logger.warning("HH employer search failed for %s: %s", company, exc)
        return None

    target = _norm_name(company)
    best = None
    best_score = -1
    for item in items:
        name = _norm_name(item.get("name") or "")
        if not name:
            continue
        score = 0
        if name == target:
            score = 100
        elif target in name or name in target:
            score = 80
        elif target.split()[0] in name:
            score = 50
        if score > best_score:
            best_score = score
            best = item
    if best_score < 50:
        return None
    return best


def search_hh_vacancy_for_employer(
    employer_id: str | int,
    *,
    title: str = "",
) -> dict[str, Any] | None:
    params: dict[str, Any] = {
        "employer_id": employer_id,
        "per_page": 10,
        "schedule": "remote",
        "order_by": "publication_time",
    }
    # Prefer FE-ish roles
    text_bits = [w for w in re.findall(r"[A-Za-zА-Яа-яёЁ]{3,}", title or "") if w.lower() not in ("the", "and")]
    fe_hint = " ".join(text_bits[:4]) if text_bits else "frontend react"
    params["text"] = fe_hint
    try:
        resp = httpx.get(HH_VACANCIES_URL, params=params, headers=_headers(), timeout=20)
        if resp.status_code != 200:
            return None
        items = resp.json().get("items") or []
    except httpx.HTTPError as exc:
        logger.warning("HH vacancy-by-employer failed %s: %s", employer_id, exc)
        return None
    if not items:
        # retry broader
        try:
            time.sleep(RATE_LIMIT_SEC)
            resp = httpx.get(
                HH_VACANCIES_URL,
                params={
                    "employer_id": employer_id,
                    "per_page": 5,
                    "order_by": "publication_time",
                },
                headers=_headers(),
                timeout=20,
            )
            items = resp.json().get("items") or [] if resp.status_code == 200 else []
        except httpx.HTTPError:
            return None
    if not items:
        return None
    # Prefer frontend titles
    def _rank(it: dict[str, Any]) -> int:
        n = (it.get("name") or "").lower()
        score = 0
        for tok in ("frontend", "front-end", "фронт", "react", "typescript", "node"):
            if tok in n:
                score += 10
        return score

    items = sorted(items, key=_rank, reverse=True)
    return items[0]


def research_direct_apply(
    company: str,
    *,
    title: str = "",
    live_hh: bool = True,
) -> dict[str, Any]:
    """
    Build direct-apply research package for a company.

    Returns links always (when company known); optionally resolves HH employer/vacancy.
    """
    company = (company or "").strip()
    links = build_research_links(company, title=title)
    result: dict[str, Any] = {
        "company": company,
        **links,
        "hh_employer_url": None,
        "hh_employer_name": None,
        "hh_vacancy_url": None,
        "hh_vacancy_title": None,
        "primary_url": None,
        "found_direct": False,
    }
    if not company:
        return result

    if live_hh:
        employer = search_hh_employer(company)
        if employer:
            result["hh_employer_url"] = employer.get("alternate_url") or (
                f"https://hh.ru/employer/{employer.get('id')}"
            )
            result["hh_employer_name"] = employer.get("name")
            time.sleep(RATE_LIMIT_SEC)
            vac = search_hh_vacancy_for_employer(employer["id"], title=title)
            if vac:
                result["hh_vacancy_url"] = vac.get("alternate_url")
                result["hh_vacancy_title"] = vac.get("name")
                result["found_direct"] = True

    # Primary: real vacancy > employer page only (never Google stubs)
    result["primary_url"] = (
        result.get("hh_vacancy_url")
        or result.get("hh_employer_url")
        or None
    )
    if result.get("hh_vacancy_url") or result.get("hh_employer_url"):
        result["found_direct"] = True
    return result


def is_google_search_url(url: str) -> bool:
    low = (url or "").lower()
    return "google.com/search" in low or "google.ru/search" in low


def is_useless_open_url(url: str) -> bool:
    """TG aggregator posts / bot mini-apps / google stubs are not useful open targets."""
    if not url:
        return True
    if is_google_search_url(url):
        return True
    if is_aggregator_url(url):
        return True
    low = url.lower()
    if re.search(r"t\.me/(runello|gmatch|getmatch)", low):
        return True
    # Channel post without external apply
    if re.search(r"t\.me/[^/]+/\d+", low) and any(
        x in low for x in ("runello", "gmatch", "getmatch")
    ):
        return True
    return False


def pick_open_url(
    *,
    source_url: str = "",
    analysis: dict[str, Any] | None = None,
) -> str:
    """Best URL for Telegram Open — real apply / post only, never Google stubs."""
    analysis = analysis or {}
    contacts = analysis.get("apply_contacts") or {}
    for u in contacts.get("direct_urls") or []:
        if not u or is_useless_open_url(u):
            continue
        if is_direct_career_url(u) or "hh.ru" in u.lower() or "fl.ru" in u.lower():
            return u
    for u in contacts.get("direct_urls") or []:
        if u and not is_useless_open_url(u):
            return u

    research = analysis.get("research") or {}
    for key in (
        "hh_vacancy_url",
        "hh_employer_url",
        "primary_url",
    ):
        u = research.get(key) or ""
        if u and not is_useless_open_url(u):
            return u

    # Prefer original post/board link over fake «search yourself» URLs
    if source_url and not is_useless_open_url(source_url):
        return source_url

    # HH search is a real board, not Google — last resort when company known
    hh_search = research.get("hh_search_url") or ""
    if hh_search and not is_useless_open_url(hh_search):
        return hh_search

    company = (analysis.get("company") or "").strip()
    if company and company not in ("—", "-", "название компании из текста"):
        return hh_search_url(company)

    return ""


def research_hint_ru(research: dict[str, Any]) -> str:
    if research.get("hh_vacancy_url"):
        title = research.get("hh_vacancy_title") or "вакансия"
        return f"На HH: {title}"
    if research.get("hh_employer_url"):
        name = research.get("hh_employer_name") or research.get("company") or "компания"
        return f"Работодатель на HH: {name}"
    if research.get("found_direct"):
        return "Есть прямая ссылка отклика"
    return ""
