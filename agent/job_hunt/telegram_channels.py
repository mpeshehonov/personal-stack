"""Public Telegram job channels via t.me/s/ web preview (read-only)."""

from __future__ import annotations

import html
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from job_hunt.apply_path import analyze_apply_path, extract_company_name
from job_hunt.config import JOBHUNT_USER_AGENT, tg_channel_names, tg_match_keywords

logger = logging.getLogger(__name__)

TG_PREVIEW_URL = "https://t.me/s/{channel}"
RATE_LIMIT_SEC = 1.5
# Drop stale posts at ingest — recruiters move on; aggregator bots are worse when old.
MAX_AGE_HOURS = 14 * 24
AGGREGATOR_MAX_AGE_HOURS = 5 * 24

_MESSAGE_SPLIT = re.compile(r'<div class="tgme_widget_message_wrap')
_TEXT_RE = re.compile(
    r'class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>',
    re.DOTALL,
)
_POST_RE = re.compile(r'data-post="(?P<channel>[^/]+)/(?P<id>\d+)"')
_DATE_RE = re.compile(r'datetime="(?P<ts>[^"]+)"')
_HREF_RE = re.compile(r'href="(?P<href>https?://[^"]+)"', re.I)
_TAG_SPLIT = re.compile(r"\s+#")


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
    }


def _strip_html(text: str) -> str:
    """Keep newlines (needed for company:/stack lines); collapse spaces per line."""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"[^\S\n]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def _extract_title(raw_text: str) -> str:
    first_line = raw_text.split("\n", 1)[0].strip()
    first_line = _TAG_SPLIT.split(first_line, 1)[0].strip(" -–—")
    if first_line and len(first_line) >= 3:
        return first_line[:200]
    match = re.search(
        r"(?P<title>(?:senior|middle|junior|lead|staff|principal|главный|старш|младш|senior/lead)?"
        r"[\s/-]*(?:frontend|front-end|react|javascript|typescript|full[\s-]?stack|web)[^\n#]{0,80})",
        raw_text,
        re.IGNORECASE,
    )
    return match.group("title").strip()[:200] if match else raw_text[:120]


def _matches_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in tg_match_keywords())


def _parse_published_at(chunk: str) -> str | None:
    m = _DATE_RE.search(chunk)
    if not m:
        return None
    raw = m.group("ts").strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return raw


def _is_fresh(published_at: str | None, *, aggregator: bool) -> bool:
    if not published_at:
        # Unknown age — keep (better than silently dropping whole channel)
        return True
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    max_h = AGGREGATOR_MAX_AGE_HOURS if aggregator else MAX_AGE_HOURS
    return datetime.now(timezone.utc) - dt <= timedelta(hours=max_h)


def tg_to_vacancy_shape(
    *,
    channel: str,
    post_id: str,
    raw_text: str,
    title: str,
    company: str,
    published_at: str | None,
    hrefs: list[str],
    apply_path: dict[str, Any],
) -> dict[str, Any]:
    remote = "удал" in raw_text.lower() or "remote" in raw_text.lower()
    post_url = f"https://t.me/{channel}/{post_id}"
    actionable = bool(apply_path.get("actionable"))
    aggregator = bool(apply_path.get("aggregator"))
    snippet = raw_text[:900]
    hint = apply_path.get("apply_hint_ru") or ""
    if hint:
        snippet = f"{snippet}\n\n[отклик] {hint}"[:1200]

    return {
        "id": f"{channel}/{post_id}",
        "name": title,
        "alternate_url": post_url,
        "employer": {"name": company},
        "key_skills": [],
        "schedule": {
            "id": "remote" if remote else "fullDay",
            "name": "удалённо" if remote else "",
        },
        "salary": None,
        "snippet": {"requirement": snippet, "responsibility": ""},
        "area": {"name": ""},
        "published_at": published_at,
        "_source": "telegram",
        "_source_channel": channel,
        "_published_at": published_at,
        "_apply_path": apply_path,
        "_aggregator": aggregator,
        "_paywall": aggregator and not actionable,
        "_actionable": actionable,
        "_apply_hint_ru": hint,
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
    skipped_stale = 0
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

        post_channel = post_m.group("channel")
        post_id = post_m.group("id")
        post_url = f"https://t.me/{post_channel}/{post_id}"
        hrefs = [m.group("href") for m in _HREF_RE.finditer(chunk)]
        published_at = _parse_published_at(chunk)

        apply_path = analyze_apply_path(
            text=raw_text,
            hrefs=hrefs,
            channel=post_channel,
            post_url=post_url,
        )
        if not _is_fresh(published_at, aggregator=bool(apply_path.get("aggregator"))):
            skipped_stale += 1
            continue

        company = apply_path.get("company") or extract_company_name(raw_text)
        results.append(
            tg_to_vacancy_shape(
                channel=post_channel,
                post_id=post_id,
                raw_text=raw_text,
                title=title,
                company=company,
                published_at=published_at,
                hrefs=hrefs,
                apply_path=apply_path,
            )
        )

    logger.info(
        "Telegram/%s: parsed %s relevant posts (skipped stale %s)",
        channel,
        len(results),
        skipped_stale,
    )
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
