"""Live CLIENT lead scan — only fresh, open orders (no dead Habr Freelance)."""

from __future__ import annotations

import html
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT
from opportunity.verticals import upsert_seed
from orchestrator.state import get_conn

logger = logging.getLogger(__name__)

TG_PREVIEW = "https://t.me/s/{channel}"
RATE_LIMIT_SEC = 1.2
MAX_AGE_HOURS = 72  # hard freshness gate

# Live-enough free sources (validated 2026-08-06). NEVER freelansim / u.habr.com.
TG_ORDER_CHANNELS = (
    "job_webdev",  # FE + kwork.ru/projects links
    "it_zakazy",  # kwork mirrors, often same-day
    "projects_fl",  # FL.ru mirror feed (text often without links)
    "kwork_projects",  # dense Kwork want feed
    "web_zakaz",
    "frilans_zakazy",
)

# Channels that are marketplace mirrors — never keep bare t.me/figma as apply URL
TG_MARKETPLACE_REQUIRED = frozenset(
    {
        "projects_fl",
        "it_zakazy",
        "kwork_projects",
        "job_webdev",
    }
)

DEAD_URL_MARKERS = (
    "freelance.habr.com",
    "u.habr.com",
    "freelansim",
    "habr.com/freelance",
)

_FL_CLOSED_MARKERS = (
    "исполнитель выбран",
    "заказ закрыт",
    "проект закрыт",
    "проект уже закрыт",
    "похожие проекты на бирже",
    "похожие проекты",
    "к сожалению, проект",
)

_KWORK_CLOSED_MARKERS = (
    "заказ закрыт",
    "проект не найден",
    "want not found",
    "проект удален",
    "проект удалён",
    "заказ выполнен",
    "исполнитель выбран",
)

_MARKETPLACE_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:fl\.ru/projects/\d+[^\s\"'<>]*|kwork\.ru/projects/\d+[^\s\"'<>]*)",
    re.I,
)

_MESSAGE_SPLIT = re.compile(r'<div class="tgme_widget_message_wrap')
_TEXT_RE = re.compile(
    r'class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>',
    re.DOTALL,
)
_POST_RE = re.compile(r'data-post="(?P<channel>[^/]+)/(?P<id>\d+)"')
_DATE_RE = re.compile(r'datetime="(?P<ts>[^"]+)"')
_HREF_RE = re.compile(r'href="(?P<href>https?://[^"]+)"', re.I)
_BUDGET_RE = re.compile(
    r"(?:бюджет|💰|💸)\s*:?\s*([^\n|]{0,40}?\d[\d\s]{0,8}\s*(?:руб|₽|₽)?)",
    re.I,
)
_FL_PUBLISHED_RE = re.compile(
    r"Опубликован\s+(\d{2})\.(\d{2})\.(\d{4})\s+в\s+(\d{2}):(\d{2})",
    re.I,
)

_STRONG = (
    "react",
    "next.js",
    "nextjs",
    "typescript",
    "frontend",
    "front-end",
    "фронтенд",
    "фронт ",
    "preact",
    "верстк",
    "админк",
    "личный кабинет",
    "mini app",
    "javascript",
)
_MEDIUM = (
    "лендинг",
    "интерфейс",
    "landing",
    "html",
    "css",
    "figma",
    "vue",
    "webflow",
    "wordpress",
    "bitrix",
    "modx",
    "tilda",
    "вёрст",
    "версталь",
)
_NEGATIVE = (
    "golang",
    "на python",
    "на питоне",
    "python-",
    "fastapi",
    "парсинг",
    "парсер",
    "android",
    "1с",
    "1c ",
    "smm ",
    "excel",
    "flutter",
    "ios ",
    "видео-шортс",
    "ролик на",
    "монтаж видео",
    "seo-специалист",
    "менеджер по переписке",
    "оператор чата",
    "таргетолог",
    "заполнению анкет",
    "размещению объявлений",
    "публикации объявлений",
    "телеграм-бота",
    "telegram-бота",
    "подборка лучших",
    "лучшие статьи",
    "не чаще, чем раз",
)


def _headers() -> dict[str, str]:
    return {
        "User-Agent": JOBHUNT_USER_AGENT,
        "Accept-Language": "ru-RU,ru;q=0.9",
    }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _strip_html(raw: str) -> str:
    text = _HREF_RE.sub(r" \g<href> ", raw)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def is_dead_url(url: str) -> bool:
    low = (url or "").lower()
    return any(m in low for m in DEAD_URL_MARKERS)


def parse_tg_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        # 2026-08-02T14:55:08+00:00
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def is_fresh(dt: datetime | None, *, max_age_hours: int = MAX_AGE_HOURS) -> bool:
    if dt is None:
        return False
    return (_utcnow() - dt) <= timedelta(hours=max_age_hours)


def score_order(title: str, body: str = "", price: str = "") -> dict[str, Any]:
    blob = f"{title} {body} {price}".lower()
    if any(n in blob for n in _NEGATIVE) and not any(s in blob for s in _STRONG[:8]):
        return {"keep": False, "score": 0, "reasons": ["мимо стека"]}

    strong = [s for s in _STRONG if s in blob]
    medium = [s for s in _MEDIUM if s in blob]
    if not strong and not medium:
        return {"keep": False, "score": 0, "reasons": ["нет FE-сигнала"]}

    score = 50
    reasons: list[str] = []
    if strong:
        score += 30
        reasons.append("стек: " + ", ".join(strong[:3]))
    elif medium:
        score += 12
        reasons.append("смежно: " + ", ".join(medium[:2]))

    # Prefer real product FE over tilda/wp-only
    if any(x in blob for x in ("react", "next", "typescript", "frontend", "фронтенд")):
        score += 10
    cms_only = any(x in blob for x in ("tilda", "wordpress", "bitrix", "modx", "webflow"))
    if cms_only and not strong and "верст" not in blob and "вёрст" not in blob:
        return {"keep": False, "score": 0, "reasons": ["CMS/no-code без FE-стека"]}

    digits = re.sub(r"\D", "", price or "")
    budget = int(digits) if digits and len(digits) <= 7 else None
    if budget is not None:
        if budget < 5000:
            return {"keep": False, "score": 0, "reasons": [f"бюджет слишком мал: {budget}₽"]}
        if budget >= 20000:
            score += 10
            reasons.append(f"бюджет ~{budget}₽")
        else:
            reasons.append(f"бюджет ~{budget}₽")
    elif price:
        reasons.append(price[:60])

    score = max(0, min(95, score))
    return {
        "keep": score >= 58,
        "score": score,
        "reasons": reasons or ["FE-заказ"],
        "budget": budget,
    }


def _title_from_html(page: str) -> str:
    m = re.search(r'property="og:title" content="([^"]+)"', page, re.I)
    if not m:
        m = re.search(r"<title>([^<]+)</title>", page, re.I)
    if not m:
        return ""
    title = html.unescape(m.group(1)).strip()
    title = re.sub(r"\s*[-–|]\s*Kwork.*$", "", title, flags=re.I)
    title = re.sub(r":\s*проект в категории.*$", "", title, flags=re.I)
    title = re.sub(r",\s*\d{2}\.\d{2}\.\d{4}.*$", "", title)
    return title.strip()[:160]


def validate_fl_project(url: str) -> dict[str, Any]:
    """Confirm FL project is open and published recently."""
    try:
        resp = httpx.get(url, headers=_headers(), timeout=25, follow_redirects=True)
    except httpx.HTTPError as exc:
        return {"ok": False, "reason": f"fetch: {exc}"}
    if resp.status_code != 200:
        return {"ok": False, "reason": f"HTTP {resp.status_code}"}
    page = resp.text
    text = _strip_html(page)
    low = text.lower()
    if any(x in low for x in _FL_CLOSED_MARKERS):
        return {"ok": False, "reason": "closed"}
    if "откликнуться" not in low:
        return {"ok": False, "reason": "no apply button"}
    pub = _FL_PUBLISHED_RE.search(text)
    published: datetime | None = None
    if pub:
        d, m, y, hh, mm = map(int, pub.groups())
        published = datetime(y, m, d, hh, mm, tzinfo=timezone.utc)
    if published and not is_fresh(published, max_age_hours=MAX_AGE_HOURS + 3):
        return {"ok": False, "reason": f"stale {published.isoformat()}"}
    title = _title_from_html(page)
    # Score TITLE only — FL detail pages are full of sidebar FE noise
    scored = score_order(title, "", "")
    if not scored.get("keep"):
        return {"ok": False, "reason": f"fe filter on title: {title[:60]}"}
    return {
        "ok": True,
        "published": published,
        "title": title,
        "snippet": text[:500],
        "scored": scored,
    }


def validate_kwork_project(url: str) -> dict[str, Any]:
    """Kwork want page must stay on /projects/<id> and look FE + open."""
    try:
        resp = httpx.get(url, headers=_headers(), timeout=25, follow_redirects=True)
    except httpx.HTTPError as exc:
        return {"ok": False, "reason": f"fetch: {exc}"}
    if resp.status_code != 200:
        return {"ok": False, "reason": f"HTTP {resp.status_code}"}
    final = str(resp.url)
    if not re.search(r"/projects/\d+", final):
        return {"ok": False, "reason": f"redirected away: {final}"}
    page = resp.text
    low = page.lower()
    if any(x in low for x in _KWORK_CLOSED_MARKERS):
        return {"ok": False, "reason": "closed"}
    # Soft signal that want is still open
    if not any(
        x in low
        for x in (
            "откликнуться",
            "оставить отклик",
            "предложи",
            "want-view",
            "data-id",
        )
    ):
        # Don't hard-fail on missing button (SPA), but closed markers above catch most
        pass
    title = _title_from_html(page)
    if not title or title.lower() in ("kwork", "проекты"):
        return {"ok": False, "reason": "no title"}
    scored = score_order(title, title)
    if not scored.get("keep"):
        return {"ok": False, "reason": f"fe filter: {title[:60]}"}
    return {"ok": True, "title": title, "snippet": title, "scored": scored}


def extract_marketplace_urls(*blobs: str) -> list[str]:
    """Pull FL/Kwork project URLs from hrefs and plain text."""
    found: list[str] = []
    for blob in blobs:
        if not blob:
            continue
        for m in _MARKETPLACE_URL_RE.finditer(blob):
            u = m.group(0).rstrip(").,;\"'")
            # normalize kwork view suffix
            u = re.sub(r"/view/?$", "", u)
            found.append(u)
    # Prefer FL then Kwork, unique
    ranked = sorted(
        dict.fromkeys(found),
        key=lambda u: (0 if "fl.ru" in u else 1, u),
    )
    return ranked


def pick_apply_url(hrefs: list[str], *, tg_fallback: str, text: str = "") -> str:
    ranked: list[tuple[int, str]] = []
    candidates = list(hrefs or []) + extract_marketplace_urls(text, " ".join(hrefs or []))
    for href in candidates:
        href = href.replace("&amp;", "&").rstrip(").,;")
        if is_dead_url(href):
            continue
        host = urlparse(href).netloc.lower()
        path = urlparse(href).path.lower()
        if "fl.ru" in host and "/projects/" in path:
            ranked.append((0, href))
        elif "kwork.ru" in host and "/projects/" in path:
            ranked.append((1, href.split("?")[0].rstrip("/")))
        elif host and "t.me" not in host and "telegram" not in host:
            # Ignore figma/docs/yandex as apply targets — not bidable orders
            if any(
                x in host
                for x in ("figma.com", "docs.google", "disk.yandex", "drive.google")
            ):
                continue
            ranked.append((3, href))
    if ranked:
        ranked.sort(key=lambda x: x[0])
        return ranked[0][1]
    return tg_fallback


def fetch_tg_posts(channel: str) -> list[dict[str, Any]]:
    channel = channel.lstrip("@").strip()
    try:
        resp = httpx.get(
            TG_PREVIEW.format(channel=channel),
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            logger.warning("client_scan TG %s HTTP %s", channel, resp.status_code)
            return []
        page = resp.text
    except httpx.HTTPError as exc:
        logger.warning("client_scan TG %s failed: %s", channel, exc)
        return []

    if "tgme_widget_message_wrap" not in page:
        return []

    out: list[dict[str, Any]] = []
    for chunk in _MESSAGE_SPLIT.split(page)[1:]:
        post_m = _POST_RE.search(chunk)
        text_m = _TEXT_RE.search(chunk)
        date_m = _DATE_RE.search(chunk)
        if not post_m or not text_m:
            continue
        hrefs = [m.group("href") for m in _HREF_RE.finditer(text_m.group("text"))]
        text = _strip_html(text_m.group("text"))
        dt = parse_tg_datetime(date_m.group("ts") if date_m else "")
        out.append(
            {
                "channel": post_m.group("channel"),
                "post_id": post_m.group("id"),
                "text": text,
                "hrefs": hrefs,
                "published": dt,
                "tg_url": f"https://t.me/{post_m.group('channel')}/{post_m.group('id')}",
            }
        )
    return out


def scan_tg_orders() -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    for idx, channel in enumerate(TG_ORDER_CHANNELS):
        if idx:
            time.sleep(RATE_LIMIT_SEC)
        for post in fetch_tg_posts(channel):
            if not is_fresh(post.get("published")):
                continue
            text = post["text"]
            low = text.lower()
            if any(
                x in low
                for x in (
                    "подборка лучших",
                    "лучшие статьи",
                    "лучшие фронтенд вакансии",
                    "вакансия",
                    "компания:",
                )
            ) and "kwork.ru/projects" not in low and "fl.ru/projects" not in low:
                # Pure vacancy digests / weekly digests without marketplace order link
                if "что нужно сделать" not in low and "бюджет" not in low:
                    continue

            title = text.split("\n", 1)[0].strip()[:160] or "FE заказ"
            budget_m = _BUDGET_RE.search(text)
            price = budget_m.group(1).strip() if budget_m else ""
            scored = score_order(title, text, price)
            if not scored.get("keep"):
                continue

            apply_url = pick_apply_url(
                post.get("hrefs") or [],
                tg_fallback=post["tg_url"],
                text=text,
            )
            if is_dead_url(apply_url):
                continue

            # Marketplace links required for quality; bare TG only if <24h + strong FE + budget
            # Aggregator mirrors (projects_fl / kwork_projects / …) NEVER keep bare t.me
            source_name = "Telegram"
            channel_l = (post.get("channel") or channel or "").lstrip("@").lower()
            requires_market = channel_l in TG_MARKETPLACE_REQUIRED
            if "fl.ru" in apply_url:
                v = validate_fl_project(apply_url)
                if not v.get("ok"):
                    continue
                source_name = "FL.ru"
                title = (v.get("title") or title)[:160]
                scored = v.get("scored") or scored
            elif "kwork.ru" in apply_url:
                v = validate_kwork_project(apply_url)
                if not v.get("ok"):
                    continue
                source_name = "Kwork"
                title = (v.get("title") or title)[:160]
                scored = v.get("scored") or scored
            else:
                if requires_market:
                    continue
                age_ok = is_fresh(post.get("published"), max_age_hours=24)
                strong = any(
                    s in low
                    for s in ("react", "frontend", "фронтенд", "typescript", "next", "верстк")
                )
                if not (age_ok and strong and ("бюджет" in low or "₽" in text or "руб" in low)):
                    continue
                source_name = f"TG/{channel}"

            path_key = urlparse(apply_url).path.strip("/").replace("/", "-")[:48]
            key = f"client:live:{path_key or post['post_id']}"
            seeds.append(
                _seed(
                    key=key,
                    title=title,
                    entity=source_name,
                    url=apply_url,
                    scored=scored,
                    price=price,
                    published=post.get("published"),
                    extra_step=(
                        f"Источник пост: {post['tg_url']}"
                        if post.get("tg_url") != apply_url
                        else ""
                    ),
                )
            )
    return seeds


def scan_fl_listing() -> list[dict[str, Any]]:
    """FL.ru open projects listing — filter FE + validate detail freshness."""
    seeds: list[dict[str, Any]] = []
    try:
        resp = httpx.get(
            "https://www.fl.ru/projects/",
            headers=_headers(),
            timeout=30,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return []
        page = resp.text
    except httpx.HTTPError as exc:
        logger.warning("FL listing failed: %s", exc)
        return []

    ids = list(dict.fromkeys(re.findall(r"/projects/(\d+)/[^\"']+\.html", page)))
    fe_hint = re.compile(
        r"react|frontend|фронт|верст|typescript|next|javascript|лендинг|сайт|html|css|админ|vue|figma|web",
        re.I,
    )
    for pid in ids[:45]:
        i = page.find(f"/projects/{pid}/")
        if i < 0:
            continue
        chunk = page[max(0, i - 900) : i + 1400]
        chunk_text = _strip_html(chunk)
        if not fe_hint.search(chunk_text):
            continue
        slug_m = re.search(rf"/projects/{pid}/([^\"']+\.html)", chunk)
        if not slug_m:
            continue
        url = f"https://www.fl.ru/projects/{pid}/{slug_m.group(1)}"
        title_m = re.search(
            rf"/projects/{pid}/[^\"']+\.html\"[^>]*>([^<]{{8,160}})</a>",
            chunk,
        )
        title = ""
        if title_m and title_m.group(1).strip().lower() not in ("откликнуться", "подробнее"):
            title = title_m.group(1).strip()
        if not title:
            title = slug_m.group(1).replace(".html", "").replace("-", " ")[:120]

        time.sleep(0.35)
        v = validate_fl_project(url)
        if not v.get("ok"):
            continue
        title = (v.get("title") or title)[:160]
        scored = v.get("scored") or score_order(title, chunk_text)
        seeds.append(
            _seed(
                key=f"client:fl:{pid}",
                title=title,
                entity="FL.ru",
                url=url,
                scored=scored,
                price="",
                published=v.get("published"),
            )
        )
    return seeds


def _seed(
    *,
    key: str,
    title: str,
    entity: str,
    url: str,
    scored: dict[str, Any],
    price: str,
    published: datetime | None,
    extra_step: str = "",
) -> dict[str, Any]:
    fit = int(scored.get("score") or 60)
    age_note = ""
    if published:
        hours = int((_utcnow() - published).total_seconds() // 3600)
        age_note = f"опубликовано ~{hours}ч назад"
    why = list(scored.get("reasons") or [])
    if age_note:
        why.insert(0, age_note)
    steps = [
        f"Открыть заказ: {url}",
        "Откликнуться сегодня (свежий заказ, не копилка ссылок)",
        "Если взял в работу — в боте «Сделано»",
    ]
    if extra_step:
        steps.insert(1, extra_step)
    return {
        "key": key,
        "type": "CLIENT",
        "title": f"Заказ: {title}"[:180],
        "entity": entity,
        "url": url,
        "why": why[:4],
        "steps": steps,
        "fit": fit,
        "income": min(90, 55 + (10 if (scored.get("budget") or 0) >= 15000 else 0)),
        "growth": 45,
        "probability": 50,
        "strategic": 72,
        "urgency": 92,
        "next": "APPLY",
        "kind": "freelance_order",
        "price": price,
    }


def purge_dead_client_opportunities() -> int:
    """Archive closed/dead CLIENT rows (Habr + revalidate FL/Kwork)."""
    try:
        from opportunity.refresh_open import revalidate_client_opportunities

        stats = revalidate_client_opportunities(limit=60)
        return int(stats.get("archived") or 0)
    except Exception as exc:
        logger.warning("purge_dead_client_opportunities skipped: %s", exc)
        return 0


def scan_client_orders(*, upsert: bool = True) -> dict[str, Any]:
    purged = purge_dead_client_opportunities()
    seeds: list[dict[str, Any]] = []
    seeds.extend(scan_fl_listing())
    seeds.extend(scan_tg_orders())

    # Dedup by URL
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for seed in sorted(seeds, key=lambda s: int(s.get("fit") or 0), reverse=True):
        url = seed.get("url") or ""
        if not url or url in seen or is_dead_url(url):
            continue
        seen.add(url)
        unique.append(seed)

    upserted = 0
    if upsert:
        for seed in unique:
            upsert_seed(seed)
            upserted += 1

    stats = {
        "purged_dead": purged,
        "kept": len(unique),
        "upserted": upserted,
        "titles": [s["title"] for s in unique[:12]],
        "sources": sorted({s.get("entity") or "?" for s in unique}),
    }
    logger.info("client_scan live: %s", stats)
    return {"stats": stats, "seeds": unique}


def ensure_client_orders() -> dict[str, Any]:
    result = scan_client_orders(upsert=True)
    return {
        "kept": result["stats"]["kept"],
        "upserted": result["stats"]["upserted"],
        "purged_dead": result["stats"]["purged_dead"],
        "titles": result["stats"].get("titles") or [],
        "channels": result["stats"].get("sources") or [],
        "sources": result["stats"].get("sources") or [],
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out = scan_client_orders(upsert=False)
    print("purged_dead(dry)", out["stats"]["purged_dead"])
    print("kept", out["stats"]["kept"], "sources", out["stats"]["sources"])
    for s in out["seeds"][:20]:
        print(f"{s['fit']:2d} | {s['entity']:10} | {s['title'][:55]} | {s['url']}")
