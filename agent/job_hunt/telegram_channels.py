"""Public Telegram job channels via t.me/s/ web preview (read-only)."""

from __future__ import annotations

import html
import logging
import re
import time
from typing import Any

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT, tg_channel_names, tg_match_keywords

logger = logging.getLogger(__name__)

TG_PREVIEW_URL = "https://t.me/s/{channel}"
RATE_LIMIT_SEC = 1.5

_MESSAGE_SPLIT = re.compile(r'<div class="tgme_widget_message_wrap')
_TEXT_RE = re.compile(
    r'class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>',
    re.DOTALL,
)
_POST_RE = re.compile(r'data-post="(?P<channel>[^/]+)/(?P<id>\d+)"')
_COMPANY_RE = re.compile(r"компания\s*:\s*(?P<company>[^\n#☑]+)", re.IGNORECASE)
_TAG_SPLIT = re.compile(r"\s+#")


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
    }


def _strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _extract_title(raw_text: str) -> str:
    first_line = raw_text.split("\n", 1)[0].strip()
    first_line = _TAG_SPLIT.split(first_line, 1)[0].strip(" -–—")
    if first_line:
        return first_line[:200]
    match = re.search(
        r"(?P<title>(?:senior|middle|junior|lead|staff|principal|главный|старш|младш|senior/lead)?"
        r"[\s/-]*(?:frontend|front-end|react|javascript|typescript|full[\s-]?stack|web)[^\n#]{0,80})",
        raw_text,
        re.IGNORECASE,
    )
    return match.group("title").strip()[:200] if match else raw_text[:120]


def _extract_company(raw_text: str) -> str:
    match = _COMPANY_RE.search(raw_text)
    if not match:
        return ""
    return match.group("company").strip(" .,")[:120]


def _matches_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in tg_match_keywords())


def tg_to_vacancy_shape(
    *,
    channel: str,
    post_id: str,
    raw_text: str,
    title: str,
    company: str,
) -> dict[str, Any]:
    remote = "удал" in raw_text.lower() or "remote" in raw_text.lower()
    return {
        "id": f"{channel}/{post_id}",
        "name": title,
        "alternate_url": f"https://t.me/{channel}/{post_id}",
        "employer": {"name": company},
        "key_skills": [],
        "schedule": {
            "id": "remote" if remote else "fullDay",
            "name": "удалённо" if remote else "",
        },
        "salary": None,
        "snippet": {"requirement": raw_text[:500], "responsibility": ""},
        "area": {"name": ""},
        "_source": "telegram",
        "_source_channel": channel,
    }


def fetch_tg_channel_vacancies(channel: str) -> list[dict[str, Any]]:
    channel = channel.lstrip("@").strip()
    if not channel:
        return []

    try:
        resp = httpx.get(
            TG_PREVIEW_URL.format(channel=channel),
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            logger.warning("Telegram preview %s returned %s", channel, resp.status_code)
            return []
        page = resp.text
    except httpx.HTTPError as exc:
        logger.warning("Telegram preview fetch failed for %s: %s", channel, exc)
        return []

    if "tgme_widget_message_wrap" not in page:
        logger.info("Telegram/%s: no public messages in preview", channel)
        return []

    results: list[dict[str, Any]] = []
    for chunk in _MESSAGE_SPLIT.split(page)[1:]:
        post_m = _POST_RE.search(chunk)
        text_m = _TEXT_RE.search(chunk)
        if not post_m or not text_m:
            continue
        raw_text = _strip_html(text_m.group("text"))
        if not raw_text or not _matches_keywords(raw_text):
            continue
        title = _extract_title(raw_text)
        if not title:
            continue
        company = _extract_company(raw_text)
        results.append(
            tg_to_vacancy_shape(
                channel=post_m.group("channel"),
                post_id=post_m.group("id"),
                raw_text=raw_text,
                title=title,
                company=company,
            )
        )

    logger.info("Telegram/%s: parsed %s relevant posts", channel, len(results))
    return results


def fetch_all_tg_vacancies(channels: list[str] | None = None) -> list[dict[str, Any]]:
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    names = channels if channels is not None else tg_channel_names()
    for idx, channel in enumerate(names):
        if idx > 0:
            time.sleep(RATE_LIMIT_SEC)
        for item in fetch_tg_channel_vacancies(channel):
            vid = str(item.get("id", ""))
            if not vid or vid in seen:
                continue
            seen.add(vid)
            merged.append(item)
    return merged
