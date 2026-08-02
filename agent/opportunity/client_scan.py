"""Free CLIENT lead scan — public TG digests (Habr Freelance etc.), no paid subs."""

from __future__ import annotations

import html
import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT
from opportunity.verticals import upsert_seed

logger = logging.getLogger(__name__)

TG_PREVIEW = "https://t.me/s/{channel}"
RATE_LIMIT_SEC = 1.4

# Primary free sources that actually have public previews with FE orders
DEFAULT_CLIENT_CHANNELS = (
    "freelansim_ru",  # Habr Freelance digests — best signal
    "job_webdev",  # FE jobs + freelance mix
)

_MESSAGE_SPLIT = re.compile(r'<div class="tgme_widget_message_wrap')
_TEXT_RE = re.compile(
    r'class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>',
    re.DOTALL,
)
_HREF_RE = re.compile(r'<a href="(?P<href>https?://[^"]+)"', re.I)
_ITEM_RE = re.compile(
    r"(?m)^\s*\d+\.\s*(?P<title>.+?)\s*\((?P<price>[^)]*)\)\s+"
    r"(?P<url>https://(?:u\.habr\.com|freelance\.habr\.com)/[^\s]+)",
)

# Strong FE / product-UI signals
_STRONG = (
    "react",
    "next.js",
    "nextjs",
    "typescript",
    "frontend",
    "front-end",
    "фронтенд",
    "фронт ",
    "фронт-",
    "preact",
    "vue",
    "админк",
    "личный кабинет",
    "mini app",
    "мини.?апп",
)
_MEDIUM = (
    "javascript",
    "js ",
    "верстк",
    "лендинг",
    "интерфейс",
    "ui ",
    "веб-прилож",
    "web app",
    "landing",
)
_NEGATIVE = (
    "golang",
    "на go ",
    "на python",
    "на питоне",
    "питоне",
    "python",
    "fastapi",
    "парсинг",
    "парсер",
    "mev bot",
    "1c ",
    "1с ",
    "битрикс24",
    "bitrix24",
    "smm ",
    "excel",
    "flutter",
    "ios ",
    "android native",
    "машинного зрения",
    "cockroachdb",
    "телеграм бота",
    "телеграмм бота",
    "тг бота",
    "tg bot",
)
_CHEAP_RE = re.compile(
    r"(\d[\d\s]{0,6})\s*(?:руб|₽)",
    re.I,
)


def _strip_html(raw: str) -> str:
    # Keep link targets as plain URLs for item parser
    text = _HREF_RE.sub(r" \g<href> ", raw)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
    }


def fetch_channel_posts(channel: str) -> list[dict[str, str]]:
    channel = channel.lstrip("@").strip()
    if not channel:
        return []
    try:
        resp = httpx.get(
            TG_PREVIEW.format(channel=channel),
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            logger.warning("client_scan %s HTTP %s", channel, resp.status_code)
            return []
        page = resp.text
    except httpx.HTTPError as exc:
        logger.warning("client_scan fetch %s failed: %s", channel, exc)
        return []

    if "tgme_widget_message_wrap" not in page:
        return []

    out: list[dict[str, str]] = []
    for chunk in _MESSAGE_SPLIT.split(page)[1:]:
        text_m = _TEXT_RE.search(chunk)
        if not text_m:
            continue
        text = _strip_html(text_m.group("text"))
        if not text:
            continue
        out.append({"channel": channel, "text": text})
    return out


def parse_habr_digest_items(post_text: str) -> list[dict[str, str]]:
    """Split Habr Freelance digest posts into individual orders."""
    items: list[dict[str, str]] = []
    category = ""
    head = "\n".join(post_text.strip().splitlines()[:3]).lower()
    if "фронтенд" in head or "frontend" in head:
        category = "frontend"
    elif "проверенных заказчиков" in head:
        category = "verified"
    elif "подборка" in head:
        category = "digest"

    for m in _ITEM_RE.finditer(post_text):
        title = m.group("title").strip()
        price = m.group("price").strip()
        url = m.group("url").rstrip(").,;")
        # Dedup duplicated URL on same line
        url = url.split()[0]
        items.append(
            {
                "title": title[:200],
                "price": price[:80],
                "url": url,
                "category": category,
                "raw": f"{title} ({price})",
            }
        )
    return items


def _budget_rub(price: str) -> int | None:
    if not price or "договор" in price.lower():
        return None
    m = _CHEAP_RE.search(price.replace("\xa0", " "))
    if not m:
        return None
    digits = re.sub(r"\D", "", m.group(1))
    if not digits:
        return None
    return int(digits)


def score_client_order(title: str, price: str, *, category: str = "") -> dict[str, Any]:
    blob = f"{title} {price}".lower()
    reasons: list[str] = []

    if any(n in blob for n in _NEGATIVE) and not any(s in blob for s in _STRONG):
        return {"keep": False, "score": 0, "reasons": ["мимо стека"]}

    strong_hits = [s for s in _STRONG if s in blob]
    medium_hits = [s for s in _MEDIUM if s in blob]
    score = 45
    if category == "frontend":
        score += 20
        reasons.append("дайджест категории Фронтенд")
    if strong_hits:
        score += 25
        reasons.append("стек: " + ", ".join(strong_hits[:3]))
    elif medium_hits:
        score += 12
        reasons.append("смежно: " + ", ".join(medium_hits[:2]))
    else:
        if category != "frontend":
            return {"keep": False, "score": 0, "reasons": ["нет FE-сигнала"]}

    budget = _budget_rub(price)
    if budget is not None:
        if budget < 5000 and "час" not in price.lower():
            return {"keep": False, "score": 0, "reasons": [f"бюджет слишком мал: {budget}₽"]}
        if budget >= 40000:
            score += 15
            reasons.append(f"бюджет {budget}₽+")
        elif budget >= 15000:
            score += 8
            reasons.append(f"бюджет ~{budget}₽")
        else:
            reasons.append(f"бюджет ~{budget}₽")
    else:
        reasons.append(price or "бюджет договорной")

    score = min(95, score)
    return {"keep": score >= 55, "score": score, "reasons": reasons, "budget": budget}


def _url_key(url: str) -> str:
    path = urlparse(url).path.strip("/") or "x"
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", path)[:40]
    return safe.lower()


def order_to_seed(item: dict[str, str], scored: dict[str, Any]) -> dict[str, Any]:
    title = item["title"]
    price = item.get("price") or ""
    url = item["url"]
    key = f"client:habr:{_url_key(url)}"
    fit = int(scored["score"])
    return {
        "key": key,
        "type": "CLIENT",
        "title": f"Заказ: {title}"[:180],
        "entity": "Habr Freelance",
        "url": url,
        "why": scored.get("reasons") or ["FE-заказ с Хабр Фриланс"],
        "steps": [
            f"Открыть заказ: {url}",
            "Откликнуться на Хабре (коротко: React/TS 7 лет + 1 кейс под задачу)",
            "Если ок — отметить в боте «Ок» / записать applied",
        ],
        "fit": fit,
        "income": min(90, 55 + (10 if (scored.get("budget") or 0) >= 15000 else 0)),
        "growth": 50,
        "probability": 45,
        "strategic": 70,
        "urgency": 85,
        "next": "APPLY",
        "kind": "freelance_order",
        "price": price,
    }


def extract_standalone_fe_posts(post_text: str, channel: str) -> list[dict[str, str]]:
    """Non-digest posts that look like a single FE freelance/project ask."""
    low = post_text.lower()
    if not any(s in low for s in _STRONG + ("верстк", "лендинг", "заказ")):
        return []
    if "подборка заказов" in low or "подборка проектов" in low:
        return []
    # Skip pure vacancy digests that are FT hiring without project signal
    if any(k in low for k in ("fulltime", "full-time", "полный день", "офис")) and not any(
        k in low for k in ("проект", "фриланс", "заказ", "part-time", "частичн")
    ):
        return []
    # Find first http link as apply url
    urls = re.findall(r"https?://[^\s]+", post_text)
    url = ""
    for u in urls:
        if "t.me/" in u and channel in u:
            continue
        url = u.rstrip(").,;")
        break
    if not url:
        url = f"https://t.me/s/{channel}"
    title = post_text.split("\n", 1)[0].strip()[:160]
    return [
        {
            "title": title or "FE заказ",
            "price": "см. пост",
            "url": url,
            "category": "standalone",
            "raw": post_text[:500],
        }
    ]


def scan_client_orders(
    *,
    channels: tuple[str, ...] | list[str] | None = None,
    upsert: bool = True,
) -> dict[str, Any]:
    channels = tuple(channels or DEFAULT_CLIENT_CHANNELS)
    seen_urls: set[str] = set()
    seeds: list[dict[str, Any]] = []
    stats = {"channels": {}, "parsed_items": 0, "kept": 0, "upserted": 0}

    for idx, channel in enumerate(channels):
        if idx:
            time.sleep(RATE_LIMIT_SEC)
        posts = fetch_channel_posts(channel)
        stats["channels"][channel] = len(posts)
        for post in posts:
            text = post["text"]
            items = parse_habr_digest_items(text)
            if not items and channel != "freelansim_ru":
                items = extract_standalone_fe_posts(text, channel)
            stats["parsed_items"] += len(items)
            for item in items:
                url = item["url"]
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                scored = score_client_order(
                    item["title"], item.get("price") or "", category=item.get("category") or ""
                )
                if not scored.get("keep"):
                    continue
                seed = order_to_seed(item, scored)
                seeds.append(seed)
                stats["kept"] += 1
                if upsert:
                    upsert_seed(seed)
                    stats["upserted"] += 1

    # Prefer higher scores first in logs
    seeds.sort(key=lambda s: int(s.get("fit") or 0), reverse=True)
    stats["titles"] = [s["title"] for s in seeds[:12]]
    logger.info(
        "client_scan: channels=%s kept=%s upserted=%s",
        stats["channels"],
        stats["kept"],
        stats["upserted"],
    )
    return {"stats": stats, "seeds": seeds}


def ensure_client_orders() -> dict[str, Any]:
    """Entry for brief/scan hooks."""
    result = scan_client_orders(upsert=True)
    return {
        "kept": result["stats"]["kept"],
        "upserted": result["stats"]["upserted"],
        "titles": result["stats"].get("titles") or [],
        "channels": result["stats"].get("channels") or {},
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out = scan_client_orders(upsert=False)
    print("channels", out["stats"]["channels"])
    print("parsed", out["stats"]["parsed_items"], "kept", out["stats"]["kept"])
    for s in out["seeds"][:15]:
        print(f"{s['fit']:2d} | {s['title'][:70]} | {s['url']}")
