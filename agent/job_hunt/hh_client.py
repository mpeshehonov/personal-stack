"""HH.ru vacancy fetch — API first, Google Translate HTML fallback when geo-blocked."""

from __future__ import annotations

import json
import logging
import re
from html import unescape
from typing import Any
from urllib.parse import quote

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT

logger = logging.getLogger(__name__)

_HH_ID_RE = re.compile(r"hh\.ru/vacancy/(\d+)", re.I)


def extract_hh_vacancy_id(url_or_text: str) -> str | None:
    m = _HH_ID_RE.search(url_or_text or "")
    return m.group(1) if m else None


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
        "HH-User-Agent": JOBHUNT_USER_AGENT,
    }


def _strip_html(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def fetch_hh_vacancy_api(vacancy_id: str) -> dict[str, Any] | None:
    try:
        resp = httpx.get(
            f"https://api.hh.ru/vacancies/{vacancy_id}",
            headers=_headers(),
            timeout=25,
        )
    except httpx.HTTPError as exc:
        logger.info("HH API network error %s: %s", vacancy_id, exc)
        return None
    if resp.status_code != 200:
        logger.info("HH API HTTP %s for %s", resp.status_code, vacancy_id)
        return None
    try:
        return resp.json()
    except json.JSONDecodeError:
        return None


def _parse_jobposting_blocks(html: str) -> dict[str, Any] | None:
    """Extract schema.org JobPosting from HH HTML (via translate mirror)."""
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if isinstance(block, dict) and block.get("@type") == "JobPosting":
                return block
            if isinstance(block, dict) and isinstance(block.get("@graph"), list):
                for node in block["@graph"]:
                    if isinstance(node, dict) and node.get("@type") == "JobPosting":
                        return node
    return None


def fetch_hh_vacancy_via_translate(vacancy_id: str) -> dict[str, Any] | None:
    """
    HH blocks NL VPS (API 403 / page 451). Google Translate still mirrors the page
    with JobPosting JSON-LD — enough for cover letters.
    """
    url = f"https://hh.ru/vacancy/{vacancy_id}"
    gt = (
        "https://translate.google.com/translate?hl=ru&sl=ru&tl=en&u="
        + quote(url, safe="")
    )
    try:
        resp = httpx.get(
            gt,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "ru-RU,ru;q=0.9",
            },
            timeout=40,
            follow_redirects=True,
        )
    except httpx.HTTPError as exc:
        logger.info("HH translate fetch failed %s: %s", vacancy_id, exc)
        return None
    if resp.status_code != 200 or len(resp.text) < 2000:
        return None

    html = resp.text
    job = _parse_jobposting_blocks(html)
    title = ""
    company = ""
    description = ""
    if job:
        title = (job.get("title") or "").strip()
        description = job.get("description") or ""
        org = job.get("hiringOrganization") or {}
        if isinstance(org, dict):
            company = (org.get("name") or "").strip()

    if not title:
        m = re.search(
            r'data-qa="vacancy-title"[^>]*>([^<]{3,200})',
            html,
            re.I,
        )
        title = unescape(m.group(1)).strip() if m else ""

    if not company:
        m = re.search(
            r'data-qa="[^"]*vacancy-company-name[^"]*"[^>]*>.*?>([^<]{2,120})',
            html,
            re.I | re.S,
        )
        if not m:
            m = re.search(
                r'data-qa="vacancy-company-name"[^>]*>([^<]{2,120})',
                html,
                re.I,
            )
        company = unescape(m.group(1)).strip() if m else ""

    desc_text = _strip_html(description) if description else ""
    if len(desc_text) < 80:
        # Fallback: vacancy-description block
        m = re.search(
            r'data-qa="vacancy-description"[^>]*>(.*?)</div>\s*</div>',
            html,
            re.I | re.S,
        )
        if m:
            desc_text = _strip_html(m.group(1))

    if not title and len(desc_text) < 80:
        return None

    return {
        "id": vacancy_id,
        "name": title or "Вакансия",
        "description": description or desc_text,
        "alternate_url": url,
        "employer": {"name": company},
        "key_skills": [],
        "_source": "hh_translate",
    }


def fetch_hh_vacancy_data(vacancy_id: str) -> dict[str, Any] | None:
    data = fetch_hh_vacancy_api(vacancy_id)
    if data:
        return data
    data = fetch_hh_vacancy_via_translate(vacancy_id)
    if data:
        logger.info("HH vacancy %s loaded via translate fallback", vacancy_id)
        return data
    return None


def vacancy_blob_from_data(data: dict[str, Any], *, vacancy_id: str = "") -> dict[str, str]:
    """Normalize API/translate payload into title/company/url/text."""
    vid = str(vacancy_id or data.get("id") or "")
    desc = _strip_html(data.get("description") or "")
    skills = [
        s.get("name", "")
        for s in (data.get("key_skills") or [])
        if isinstance(s, dict) and s.get("name")
    ]
    company = ((data.get("employer") or {}).get("name")) or ""
    title = data.get("name") or ""
    url = data.get("alternate_url") or (f"https://hh.ru/vacancy/{vid}" if vid else "")
    blob = "\n".join(
        [
            f"Вакансия: {title}",
            f"Компания: {company}",
            f"URL: {url}",
            "Стек/навыки: " + ", ".join(skills),
            desc,
        ]
    )
    return {
        "title": title,
        "company": company,
        "url": url,
        "text": blob[:12000],
        "description": desc[:5000],
        "source": str(data.get("_source") or "hh"),
    }
