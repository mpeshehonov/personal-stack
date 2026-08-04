"""How to actually apply: prefer direct TG/email/career URL over aggregator bots."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Channels / bots / hosts where "Откликнуться" is almost certainly a black hole.
AGGREGATOR_CHANNELS = frozenset(
    {
        "runello_rus_frontend",
        "runello_jobs",
        "runello",
        "gmatch",
        "gmatch_jobs",
        "getmatch",
        "getmatch_jobs",
    }
)

AGGREGATOR_HANDLES = frozenset(
    {
        "runellobot",
        "runello",
        "gmatchbot",
        "getmatch",
        "getmatchbot",
        "hirifybot",
        "habr_career_bot",
    }
)

AGGREGATOR_HOST_MARKERS = (
    "runello.ru",
    "runellobot",
    "gmatch.",
    "getmatch.ru",
    "getmatch.",
)

# Prefer these as real apply destinations.
DIRECT_HOST_MARKERS = (
    "hh.ru",
    "career.habr.com",
    "habr.com/ru/companies",
    "habr.com/companies",
    "linkedin.com/jobs",
    "ashbyhq.com",
    "boards.greenhouse.io",
    "greenhouse.io",
    "jobs.lever.co",
    "lever.co",
    "jobs.ashbyhq.com",
    "workable.com",
    "teamly.ru",
    "huntflow",
    "notion.site",
    "careers.",
    "/careers",
    "/vacancy",
    "/jobs/",
)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_TG_HANDLE_RE = re.compile(r"(?<![/\w])@([a-zA-Z][a-zA-Z0-9_]{3,31})\b")
_TG_LINK_RE = re.compile(
    r"(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z][a-zA-Z0-9_]{3,31})(?:/\d+)?",
    re.I,
)
_COMPANY_PATTERNS = (
    re.compile(r"(?i)компани[яи]\s*:\s*([^\n#|•]{2,80})"),
    re.compile(r"(?i)company\s*:\s*([^\n#|•]{2,80})"),
    re.compile(r"(?i)компани[яи]\s+[«\"]([^»\"]{2,80})[»\"]"),
    re.compile(r"(?i)employer\s*:\s*([^\n#|•]{2,80})"),
)


def extract_company_name(text: str) -> str:
    for pat in _COMPANY_PATTERNS:
        m = pat.search(text or "")
        if m:
            return m.group(1).strip(" .,;:-")[:120]
    # Title crumbs: «… в Эйчартех», «Frontend в Acme»
    first = (text or "").split("\n", 1)[0].strip()
    m = re.search(
        r"(?i)\bв\s+([A-ZА-ЯЁ][\wA-ZА-ЯЁа-яё.&+\-]{2,40})\s*$",
        first,
    )
    if m:
        name = m.group(1).strip(" .,;:-")
        if name.lower() not in ("удалёнке", "удаленке", "офисе", "команде", "продукте"):
            return name[:120]
    return ""


def _host(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def is_aggregator_url(url: str) -> bool:
    low = (url or "").lower()
    if any(m in low for m in AGGREGATOR_HOST_MARKERS):
        return True
    # Mini App / startapp deep links into aggregator bots
    if "t.me/" in low and any(b in low for b in ("runello", "gmatch", "getmatch")):
        return True
    return False


def is_direct_career_url(url: str) -> bool:
    if not url or is_aggregator_url(url):
        return False
    low = url.lower()
    # Ignore telegram channel permalinks themselves
    if "t.me/" in low or "telegram.me/" in low:
        handle = ""
        m = _TG_LINK_RE.search(url)
        if m:
            handle = m.group(1).lower()
        if handle in AGGREGATOR_HANDLES or handle in AGGREGATOR_CHANNELS:
            return False
        # Personal/recruiter TG without /digits post id — treat as contact, not career URL
        if m and "/" not in url.rstrip("/").split("t.me/", 1)[-1].split("/", 1)[-1:]:
            return False
        # Channel post links are not apply destinations
        if re.search(r"t\.me/[^/]+/\d+", low):
            return False
    return any(m in low for m in DIRECT_HOST_MARKERS)


def _unique(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def analyze_apply_path(
    *,
    text: str,
    hrefs: list[str] | None = None,
    channel: str = "",
    post_url: str = "",
) -> dict[str, Any]:
    """Classify best apply path for a vacancy post/card."""
    text = text or ""
    hrefs = list(hrefs or [])
    channel_l = (channel or "").lstrip("@").lower()
    aggregator_channel = channel_l in AGGREGATOR_CHANNELS

    emails = _unique(_EMAIL_RE.findall(text))
    # Drop noreply / aggregator mails
    emails = [
        e
        for e in emails
        if not any(x in e.lower() for x in ("noreply", "no-reply", "runello", "gmatch"))
    ]

    handles: list[str] = []
    for m in _TG_HANDLE_RE.finditer(text):
        handles.append(m.group(1))
    for m in _TG_LINK_RE.finditer(text + "\n" + "\n".join(hrefs)):
        handles.append(m.group(1))
    telegrams: list[str] = []
    for h in handles:
        hl = h.lower()
        if hl in AGGREGATOR_HANDLES or hl in AGGREGATOR_CHANNELS:
            continue
        if hl == channel_l:
            continue
        # Sibling aggregator channels / bots (runello_rus_html, gmatch_*, …)
        if any(
            hl.startswith(p) or p in hl
            for p in ("runello", "gmatch", "getmatch", "hirify")
        ):
            continue
        # Skip common noise
        if hl in ("telegram", "durov", "botfather"):
            continue
        if hl.endswith("bot"):
            if any(x in hl for x in ("job", "vacanc", "hire", "career", "hh_", "runello", "gmatch")):
                continue
        telegrams.append("@" + h.lstrip("@"))
    telegrams = _unique(telegrams)

    aggregator_urls = _unique([u for u in hrefs if is_aggregator_url(u)])
    direct_urls = _unique(
        [u for u in hrefs if is_direct_career_url(u) and u != post_url]
    )
    # Mentions of hh/career in plain text without href
    for m in re.finditer(
        r"https?://[^\s<>\"']+(?:hh\.ru|career\.habr|ashbyhq|greenhouse|lever\.co)[^\s<>\"']*",
        text,
        re.I,
    ):
        u = m.group(0).rstrip(").,;")
        if is_direct_career_url(u):
            direct_urls.append(u)
    direct_urls = _unique(direct_urls)

    company = extract_company_name(text)
    has_direct = bool(telegrams or emails or direct_urls)
    aggregator = aggregator_channel or bool(aggregator_urls) or bool(
        re.search(r"(?i)отклик\w*\s+через\s+(runello|gmatch|getmatch)", text)
    )

    if telegrams:
        strategy = "direct_tg"
        actionable = True
    elif emails:
        strategy = "direct_email"
        actionable = True
    elif direct_urls:
        strategy = "direct_url"
        actionable = True
    elif company or aggregator:
        strategy = "research_company"
        actionable = False
    else:
        strategy = "weak"
        actionable = False

    # Aggregator-only apply is never a good path even if Mini App link exists
    if aggregator and not has_direct:
        strategy = "research_company"
        actionable = False

    hint = _hint_ru(
        strategy=strategy,
        telegrams=telegrams,
        emails=emails,
        direct_urls=direct_urls,
        company=company,
        aggregator=aggregator,
    )

    return {
        "strategy": strategy,
        "actionable": actionable,
        "aggregator": aggregator,
        "company": company,
        "telegrams": telegrams,
        "emails": emails,
        "direct_urls": direct_urls,
        "aggregator_urls": aggregator_urls,
        "apply_hint_ru": hint,
    }


def _hint_ru(
    *,
    strategy: str,
    telegrams: list[str],
    emails: list[str],
    direct_urls: list[str],
    company: str,
    aggregator: bool,
) -> str:
    if strategy == "direct_tg":
        return f"Пиши в ЛС: {', '.join(telegrams[:3])} (не через агрегатор)"
    if strategy == "direct_email":
        return f"Пиши на почту: {', '.join(emails[:2])}"
    if strategy == "direct_url":
        return f"Прямой отклик: {direct_urls[0]}"
    if aggregator:
        co = company or "название компании из текста"
        return (
            f"Не через Runello/gmatch/бот. Возьми «{co}» → сайт/карьера/HH/LinkedIn → "
            "мыло или TG HR в личку"
        )
    if company:
        return (
            f"Контакта в посте нет. «{company}» → сайт/HH/LinkedIn → мыло или TG в ЛС"
        )
    return "Контакта нет — вытащи компанию из текста и ищи прямой отклик мимо канала"


def apply_contacts_blob(path: dict[str, Any]) -> str:
    """Short block for description / cover context."""
    parts: list[str] = []
    if path.get("telegrams"):
        parts.append("TG: " + ", ".join(path["telegrams"][:4]))
    if path.get("emails"):
        parts.append("Email: " + ", ".join(path["emails"][:2]))
    if path.get("direct_urls"):
        parts.append("URL: " + path["direct_urls"][0])
    if path.get("apply_hint_ru"):
        parts.append(path["apply_hint_ru"])
    return " | ".join(parts)
