"""Unified cover drafting: lead id / vacancy URL / pasted JD → copy-ready text."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT
from job_hunt.drafter import (
    Channel,
    draft_cover_letter,
    humanize_cover_text,
    vacancy_text_from_lead,
)
from orchestrator.config import AGENT_DIR
from orchestrator.state import get_job_lead

logger = logging.getLogger(__name__)

ChannelName = Literal["hh", "tg", "email"]

SKILL_PATH = AGENT_DIR / "skills" / "cover-letter" / "SKILL.md"
NOTES_PATH = AGENT_DIR / "memory" / "career-copy-notes.md"

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
_HH_ID_RE = re.compile(r"hh\.ru/vacancy/(\d+)", re.I)
_HIRIFY_RE = re.compile(r"hirify\.me/jobs/([a-zA-Z0-9\-]+)", re.I)

_CHANNEL_ALIASES = {
    "hh": "hh",
    "хх": "hh",
    "habr": "hh",
    "хабр": "hh",
    "tg": "tg",
    "telegram": "tg",
    "телега": "tg",
    "тг": "tg",
    "email": "email",
    "mail": "email",
    "e": "email",
    "почта": "email",
}


@dataclass
class CoverRequest:
    channel: ChannelName = "tg"
    lead_id: int | None = None
    urls: list[str] = field(default_factory=list)
    vacancy_text: str = ""
    raw_only: bool = False
    source_hint: str = ""


@dataclass
class VacancyPayload:
    title: str
    company: str
    url: str
    text: str
    source: str
    lead_id: int | None = None


def looks_like_cover_request(text: str) -> bool:
    low = (text or "").lower()
    if not any(k in low for k in ("сопровод", "cover", "сопроводительн")):
        return False
    if _URL_RE.search(text or ""):
        return True
    if re.search(r"#?\b\d{1,5}\b", text or ""):
        return True
    # Long pasted JD
    return len((text or "").strip()) >= 180


def parse_cover_request(raw: str) -> CoverRequest:
    text = (raw or "").strip()
    # Strip leading /cover or /ask
    text = re.sub(r"^/(cover|ask)\s*", "", text, flags=re.I).strip()

    raw_only = bool(
        re.search(r"без\s+(своих\s+)?комментари", text, re.I)
        or re.search(r"только\s+текст", text, re.I)
        or re.search(r"готов(ый|ое)?\s+для\s+копир", text, re.I)
    )

    urls = [u.rstrip(").,;") for u in _URL_RE.findall(text)]
    channel: ChannelName = "tg"
    tokens = text.split()
    consumed: set[int] = set()

    for i, tok in enumerate(tokens):
        key = tok.lower().strip(",.;:")
        if key in _CHANNEL_ALIASES:
            channel = _CHANNEL_ALIASES[key]  # type: ignore[assignment]
            consumed.add(i)
            continue
        # «для хх» / «для тг» / «отклика на хх»
        if key in ("для", "на", "канал") and i + 1 < len(tokens):
            nxt = tokens[i + 1].lower().strip(",.;:")
            if nxt in _CHANNEL_ALIASES:
                channel = _CHANNEL_ALIASES[nxt]  # type: ignore[assignment]
                consumed.add(i)
                consumed.add(i + 1)

    # Explicit HH context from phrase
    if re.search(r"\b(хх|hh\.?ru|habr|хабр)\b", text, re.I) and channel == "tg":
        if not re.search(r"\b(тг|tg|telegram|телег)\b", text, re.I):
            channel = "hh"
    if re.search(r"\b(email|почт|письм)\b", text, re.I):
        channel = "email"

    lead_id: int | None = None
    id_match = re.search(r"(?:^|\s)#?(\d{1,5})(?:\s|$)", text)
    if id_match and not urls:
        # Prefer id only when no URL (URL may contain digits)
        candidate = int(id_match.group(1))
        # Avoid treating salary-like numbers in pasted JD as ids when text is long
        if len(text) < 400 or re.search(r"(?:сопровод|cover)\s+#?\d{1,5}\b", text, re.I):
            lead_id = candidate

    # Remove boilerplate phrases for vacancy_text residue
    residue = text
    for u in urls:
        residue = residue.replace(u, " ")
    residue = re.sub(
        r"(?i)\b(нужен|нужна|нужно|сделай|напиши|сопровод|сопроводительн\w*|cover|"
        r"для\s+отклика|отклик\w*|готов\w*\s+для\s+копир\w*|без\s+(своих\s+)?комментари\w*|"
        r"только\s+текст|ваканси\w*|в\s+тг|в\s+телег\w*|на\s+хх|на\s+hh|"
        r"канал\s+\w+)\b",
        " ",
        residue,
    )
    residue = re.sub(r"\s+", " ", residue).strip(" .,;:-")

    return CoverRequest(
        channel=channel,
        lead_id=lead_id,
        urls=urls,
        vacancy_text=residue,
        raw_only=raw_only,
        source_hint=text[:120],
    )


def _strip_html(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def fetch_hh_vacancy(vacancy_id: str) -> VacancyPayload | None:
    try:
        resp = httpx.get(
            f"https://api.hh.ru/vacancies/{vacancy_id}",
            headers={"User-Agent": JOBHUNT_USER_AGENT},
            timeout=25,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
    except httpx.HTTPError:
        return None
    desc = _strip_html(data.get("description") or "")
    skills = [s.get("name", "") for s in (data.get("key_skills") or []) if s.get("name")]
    company = ((data.get("employer") or {}).get("name")) or ""
    title = data.get("name") or ""
    url = data.get("alternate_url") or f"https://hh.ru/vacancy/{vacancy_id}"
    blob = "\n".join(
        [
            f"Вакансия: {title}",
            f"Компания: {company}",
            f"URL: {url}",
            "Стек/навыки: " + ", ".join(skills),
            desc,
        ]
    )
    return VacancyPayload(
        title=title,
        company=company,
        url=url,
        text=blob[:12000],
        source="hh",
    )


def fetch_hirify_vacancy(slug: str) -> VacancyPayload | None:
    """Best-effort: Hirify public page HTML (API often paywalled for full text)."""
    url = f"https://hirify.me/jobs/{slug}"
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"},
            timeout=25,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        html = resp.text
    except httpx.HTTPError:
        return None

    title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = (title_m.group(1) if title_m else slug).split("|")[0].strip()
    title = re.sub(r"\s*[-–—]\s*Hirify.*$", "", title, flags=re.I).strip()
    text = _strip_html(html)
    # Drop nav noise
    if len(text) > 500:
        text = text[:8000]
    return VacancyPayload(
        title=title or "Frontend",
        company="",
        url=url,
        text=f"Вакансия (Hirify): {title}\nURL: {url}\n\n{text}",
        source="hirify",
    )


def fetch_generic_url(url: str) -> VacancyPayload | None:
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": JOBHUNT_USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"},
            timeout=25,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        text = _strip_html(resp.text)[:8000]
    except httpx.HTTPError:
        return None
    if len(text) < 80:
        return None
    host = urlparse(url).netloc
    return VacancyPayload(
        title="Вакансия",
        company="",
        url=url,
        text=f"Источник: {host}\nURL: {url}\n\n{text}",
        source="url",
    )


def resolve_vacancy(req: CoverRequest) -> VacancyPayload:
    if req.lead_id is not None:
        row = get_job_lead(req.lead_id)
        if not row:
            raise KeyError(f"Лид #{req.lead_id} не найден")
        lead = dict(row)
        text = vacancy_text_from_lead(lead)
        if lead.get("source") == "hh" and lead.get("external_id"):
            fetched = fetch_hh_vacancy(str(lead["external_id"]))
            if fetched:
                fetched.lead_id = req.lead_id
                return fetched
        return VacancyPayload(
            title=lead.get("title") or "Frontend",
            company=lead.get("company") or "",
            url=lead.get("url") or "",
            text=text or f"{lead.get('title')} {lead.get('company')}",
            source="lead",
            lead_id=req.lead_id,
        )

    for url in req.urls:
        hh = _HH_ID_RE.search(url)
        if hh:
            payload = fetch_hh_vacancy(hh.group(1))
            if payload:
                return payload
        hir = _HIRIFY_RE.search(url)
        if hir:
            payload = fetch_hirify_vacancy(hir.group(1))
            if payload:
                return payload
        payload = fetch_generic_url(url)
        if payload:
            return payload

    if req.vacancy_text and len(req.vacancy_text) >= 40:
        # Try extract title/company heuristics
        title = ""
        company = ""
        for line in req.vacancy_text.splitlines()[:12]:
            low = line.lower()
            if "компани" in low and ":" in line:
                company = line.split(":", 1)[1].strip()
            if not title and any(
                k in low for k in ("frontend", "фронт", "react", "senior", "middle", "разработ")
            ):
                title = line.strip()[:120]
        return VacancyPayload(
            title=title or "Frontend",
            company=company,
            url=req.urls[0] if req.urls else "",
            text=req.vacancy_text[:12000],
            source="paste",
        )

    raise ValueError(
        "Не понял вакансию. Примеры:\n"
        "/cover 42 tg\n"
        "/cover hh https://hh.ru/vacancy/…\n"
        "/cover tg <вставь текст вакансии>\n"
        "или: сопровод для хх + ссылка/текст"
    )


def _lead_dict_from_payload(payload: VacancyPayload) -> dict[str, Any]:
    return {
        "title": payload.title,
        "company": payload.company,
        "url": payload.url,
        "description_snippet": payload.text[:2000],
        "skills_json": "[]",
        "source": payload.source if payload.source in ("hh", "habr") else "paste",
        "external_id": "",
    }


def draft_cover_rules(payload: VacancyPayload, channel: ChannelName) -> dict[str, str]:
    """Deterministic fallback (improved drafter)."""
    # Map tg → email structure (full letter), hh → hh
    draft_channel: Channel = "email" if channel in ("tg", "email") else "hh"
    draft = draft_cover_letter(_lead_dict_from_payload(payload), channel=draft_channel)
    if channel == "tg":
        draft["channel"] = "tg"
    body = draft["body"]
    # HH must not be ultra-short: expand if drafter returned tiny stub
    if channel == "hh" and len(body) < 600:
        draft = draft_cover_letter(_lead_dict_from_payload(payload), channel="email")
        body = draft["body"]
        # Strip greeting for HH form optional — keep if present, OK for HH too
        draft["channel"] = "hh"
        draft["body"] = humanize_cover_text(body)
        draft["subject"] = ""
    else:
        draft["body"] = humanize_cover_text(body)
    return draft


def _read_text(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")[:limit]


def build_llm_cover_prompt(payload: VacancyPayload, channel: ChannelName) -> str:
    skill = _read_text(SKILL_PATH, 14000)
    notes = _read_text(NOTES_PATH, 4000)
    channel_rules = {
        "hh": (
            "Канал: HH/Habr поле сопроводительного. "
            "Цель 900-1500 символов, 3-5 абзацев. "
            "НЕ пиши текст короче 700 символов. Лимит 400/500 — миф."
        ),
        "tg": (
            "Канал: Telegram ЛС. С приветствием и подписью. "
            "Цель 700-1200 символов, готово к копипасту."
        ),
        "email": (
            "Канал: email. Сначала строка Тема: … затем тело 120-180 слов."
        ),
    }[channel]
    return f"""Режим: СОПРОВОДИТЕЛЬНОЕ ПИСЬМО. Только это.

{channel_rules}

Обязательно:
1. Следуй skill ниже (предлоги «в X5 / в Citilink / в НЛМК», не «на»).
2. Факты только из career-copy-notes / вакансии / резюме-контекста skill.
3. Один главный кейс под JD + при необходимости второй короткий.
4. Выдай ТОЛЬКО готовый текст для копирования (для email можно «Тема:» первой строкой).
5. Без markdown-заголовков, без «match notes», без советов «отправь сам».
6. Без длинного тире, стрелок, emoji.

Вакансия (title={payload.title!r}, company={payload.company!r}, url={payload.url!r}):
---
{payload.text[:9000]}
---

career-copy-notes:
---
{notes}
---

cover-letter skill:
---
{skill}
---
"""


def draft_cover_llm(payload: VacancyPayload, channel: ChannelName) -> str | None:
    try:
        from orchestrator.cursor_runner import run_cursor_prompt
    except Exception:
        return None
    prompt = build_llm_cover_prompt(payload, channel)
    try:
        text = run_cursor_prompt(
            prompt,
            one_shot=True,
            owner="cover",
            agent_kv_key="cursor_agent_cover",
            reset_agent=True,
        )
    except Exception as exc:
        logger.exception("LLM cover failed: %s", exc)
        return None
    if not text or text.startswith("Cursor ") or text.startswith("Run failed"):
        return None
    # Strip accidental fences / meta
    out = text.strip()
    out = re.sub(r"^```\w*\n?", "", out)
    out = re.sub(r"\n?```$", "", out)
    # Drop leading meta lines
    lines = out.splitlines()
    while lines and re.match(
        r"(?i)^(вот|ниже|сопровод|готово|match|#+\s)", lines[0].strip()
    ):
        lines.pop(0)
    out = "\n".join(lines).strip()
    if len(out) < 80:
        return None
    return humanize_cover_text(out)


def produce_cover(
    raw_input: str,
    *,
    use_llm: bool = True,
    channel_override: ChannelName | None = None,
) -> dict[str, Any]:
    req = parse_cover_request(raw_input)
    if channel_override:
        req.channel = channel_override
    payload = resolve_vacancy(req)

    body: str | None = None
    engine = "rules"
    if use_llm:
        body = draft_cover_llm(payload, req.channel)
        # Reject mythical ultra-short HH covers from the model
        if body and req.channel == "hh" and len(body) < 700:
            logger.warning("LLM HH cover too short (%s chars), falling back to rules", len(body))
            body = None
        if body:
            engine = "llm"

    draft: dict[str, str]
    if body:
        draft = {
            "title": payload.title,
            "company": payload.company or "—",
            "channel": req.channel,
            "subject": "",
            "body": body,
            "hook_kind": engine,
            "url": payload.url,
        }
        if req.channel == "email":
            m = re.match(r"(?i)^тема:\s*(.+)$", body.splitlines()[0].strip())
            if m:
                draft["subject"] = m.group(1).strip()
    else:
        draft = draft_cover_rules(payload, req.channel)
        engine = "rules"

    return {
        "request": req,
        "payload": payload,
        "draft": draft,
        "engine": engine,
        "raw_only": req.raw_only,
    }


def format_cover_reply(result: dict[str, Any]) -> str:
    draft = result["draft"]
    payload: VacancyPayload = result["payload"]
    req: CoverRequest = result["request"]
    if result.get("raw_only"):
        return draft["body"]

    lead_bit = f" #{payload.lead_id}" if payload.lead_id else ""
    channel_label = {
        "hh": "HH/Habr (~900-1500 символов, не 500)",
        "tg": "Telegram",
        "email": "email",
    }.get(draft.get("channel") or req.channel, req.channel)

    lines = [
        f"Сопровод{lead_bit} · {draft.get('company') or '—'} / {draft.get('title') or '—'}",
        f"Канал: {channel_label} · движок: {result.get('engine')}",
    ]
    if payload.url:
        lines.append(f"Вакансия: {payload.url}")
    if draft.get("subject"):
        lines.append(f"Тема: {draft['subject']}")
    lines.extend(["", "```", draft["body"], "```", "", "Отправь сам."])
    return "\n".join(lines)
