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
from job_hunt.hh_client import (
    extract_hh_vacancy_id,
    fetch_hh_vacancy_data,
    vacancy_blob_from_data,
)
from orchestrator.config import AGENT_DIR
from orchestrator.state import get_job_lead

logger = logging.getLogger(__name__)

ChannelName = Literal["hh", "tg", "email"]

SKILL_PATH = AGENT_DIR / "skills" / "cover-letter" / "SKILL.md"
NOTES_PATH = AGENT_DIR / "memory" / "career-copy-notes.md"

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
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


def _extract_jd_meta(vacancy_text: str) -> tuple[str, str]:
    """Line-aware title/company from pasted JD. Never split the whole blob on ':'."""
    title = ""
    company = ""
    for raw_line in (vacancy_text or "").splitlines()[:20]:
        line = raw_line.strip()
        if not line:
            continue
        low = line.lower()
        m_co = re.match(r"(?i)^компани[яи]\s*:\s*(.+)$", line)
        if m_co and not company:
            company = m_co.group(1).strip()[:120]
            continue
        if not title and re.match(
            r"(?i)^(senior|middle|junior|lead|staff|principal|frontend|front-end|"
            r"фронтенд|разработчик|react)",
            line,
        ):
            title = line[:160]
            continue
        if not title and any(
            k in low for k in ("frontend", "фронт", "react", "разработ")
        ):
            title = line[:160]
    if not title:
        for raw_line in (vacancy_text or "").splitlines():
            line = raw_line.strip()
            if line and not re.match(r"(?i)^(компани|локаци|формат|зарплат|стек)", line):
                title = line[:160]
                break
    return title or "Frontend", company


def parse_cover_request(raw: str) -> CoverRequest:
    text = (raw or "").strip()
    # Strip leading /cover or /ask (keep the rest of the message intact, incl. newlines)
    text = re.sub(r"^/(cover|ask)\b\s*", "", text, flags=re.I).strip()

    # Always copy-ready body by default; meta goes in a separate Telegram message.
    raw_only = True

    urls = [u.rstrip(").,;") for u in _URL_RE.findall(text)]
    channel: ChannelName = "tg"
    channel_explicit = False

    # Channel as first token: `/cover tg …` or `/cover hh https://…`
    first_line, *rest_lines = text.splitlines() or [""]
    first_tokens = first_line.split()
    consumed_prefix = ""
    if first_tokens:
        head = first_tokens[0].lower().strip(",.;:")
        if head in _CHANNEL_ALIASES:
            channel = _CHANNEL_ALIASES[head]  # type: ignore[assignment]
            channel_explicit = True
            consumed_prefix = first_tokens[0]
            first_line = first_line[len(first_tokens[0]) :].lstrip()
        elif (
            len(first_tokens) >= 2
            and first_tokens[0].lower() in ("для", "на", "канал")
            and first_tokens[1].lower().strip(",.;:") in _CHANNEL_ALIASES
        ):
            channel = _CHANNEL_ALIASES[first_tokens[1].lower().strip(",.;:")]  # type: ignore[assignment]
            channel_explicit = True
            # drop «для tg» from first line
            first_line = " ".join(first_tokens[2:]).lstrip()

    # Short commands: `/cover 42 hh` — channel may be a later token
    if not channel_explicit and len(text) < 120:
        for tok in text.split():
            key = tok.lower().strip(",.;:")
            if key in _CHANNEL_ALIASES:
                channel = _CHANNEL_ALIASES[key]  # type: ignore[assignment]
                channel_explicit = True
                break

    # Phrase / URL hints only when user did not name the channel
    if not channel_explicit:
        head_blob = " ".join((first_line, *(rest_lines[:2]))).lower()
        if re.search(r"\b(хх|hh\.?ru|habr|хабр)\b", head_blob) and not re.search(
            r"\b(тг|tg|telegram|телег)\b", head_blob
        ):
            channel = "hh"
        if re.search(r"\b(email|почт|письм)\b", head_blob):
            channel = "email"

    # Rebuild text without the channel prefix token
    body_lines = ([first_line] if first_line.strip() else []) + rest_lines
    body = "\n".join(body_lines).strip()

    lead_id: int | None = None
    # Lead id only from short command forms, not from salary numbers inside JD
    if not urls and len(body) < 200:
        id_match = re.search(
            r"(?i)(?:^|\b(?:сопровод|cover|лид)\s+)#?(\d{1,5})\b",
            body.strip(),
        )
        if not id_match:
            id_match = re.match(r"^#?(\d{1,5})\b", body.strip())
        if id_match:
            lead_id = int(id_match.group(1))
            # Drop id token from vacancy residue when command is short
            residue_candidate = re.sub(
                r"(?i)^(?:сопровод|cover|лид)?\s*#?\d{1,5}\b[\s,]*",
                "",
                body.strip(),
            ).strip()
            if len(residue_candidate) < 40:
                body = residue_candidate

    # Vacancy text: keep newlines; strip only command boilerplate on first line
    residue = body
    for u in urls:
        residue = residue.replace(u, " ").strip()
    # Drop leftover command crumbs on the first line only
    lines = residue.splitlines()
    if lines:
        lines[0] = re.sub(
            r"(?i)^\s*(нужен|нужна|нужно|сделай|напиши|сопровод|сопроводительн\w*|"
            r"cover|для\s+отклика|отклик\w*|готов\w*\s+для\s+копир\w*|"
            r"без\s+(своих\s+)?комментари\w*|только\s+текст)\b[\s,.:;-]*",
            "",
            lines[0],
        ).strip()
        # If first line is only a channel alias leftover, drop it
        if lines[0].lower().strip(",.;:") in _CHANNEL_ALIASES:
            lines = lines[1:]
    residue = "\n".join(lines).strip()
    # Collapse insane spaces but KEEP newlines
    residue = re.sub(r"[^\S\n]+", " ", residue)
    residue = re.sub(r"\n{3,}", "\n\n", residue).strip(" .,;:-")

    return CoverRequest(
        channel=channel,
        lead_id=lead_id,
        urls=urls,
        vacancy_text=residue,
        raw_only=raw_only,
        source_hint=(consumed_prefix + " " + text[:100]).strip(),
    )


def _strip_html(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def fetch_hh_vacancy(vacancy_id: str) -> VacancyPayload | None:
    data = fetch_hh_vacancy_data(vacancy_id)
    if not data:
        return None
    norm = vacancy_blob_from_data(data, vacancy_id=vacancy_id)
    return VacancyPayload(
        title=norm["title"],
        company=norm["company"],
        url=norm["url"],
        text=norm["text"],
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

    hh_urls_failed: list[str] = []
    for url in req.urls:
        hh_id = extract_hh_vacancy_id(url)
        if hh_id:
            payload = fetch_hh_vacancy(hh_id)
            if payload:
                return payload
            hh_urls_failed.append(hh_id)
            continue
        hir = _HIRIFY_RE.search(url)
        if hir:
            payload = fetch_hirify_vacancy(hir.group(1))
            if payload:
                return payload
        payload = fetch_generic_url(url)
        if payload:
            return payload

    if req.vacancy_text and len(req.vacancy_text) >= 40:
        title, company = _extract_jd_meta(req.vacancy_text)
        return VacancyPayload(
            title=title,
            company=company,
            url=req.urls[0] if req.urls else "",
            text=req.vacancy_text[:12000],
            source="paste",
        )

    if hh_urls_failed:
        vids = ", ".join(hh_urls_failed[:3])
        raise ValueError(
            f"HH вакансию {vids} не удалось открыть (API/страница с сервера часто закрыты).\n"
            "Скопируй текст вакансии с HH и пришли так:\n"
            "/cover tg\n"
            "<вставь текст>\n\n"
            "Или: /cover 42 tg — если вакансия уже есть в /jobs"
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
4. Выдай ТОЛЬКО готовый текст сопровода для копирования. Ничего больше.
5. ЗАПРЕЩЕНО в ответе: заголовки вроде «Сопровод», «Канал», «движок», «Отправь сам»,
   markdown ```, match notes, пересказ вакансии, советы, комментарии агента.
6. Без длинного тире, стрелок, emoji.
7. Для email можно первой строкой «Тема: …», затем пустая строка и тело.

Компания: {payload.company or '—'}
Должность: {payload.title or '—'}
URL: {payload.url or '—'}

Текст вакансии:
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
    out = re.sub(r"```+", "", out)
    # Drop leading/trailing agent meta — never ship this to the user in body
    lines = [ln for ln in out.splitlines()]
    while lines and re.match(
        r"(?i)^(вот|ниже|сопровод|готово|match|#+\s|канал:|движок:|meta:|отправь сам)",
        lines[0].strip(),
    ):
        lines.pop(0)
    while lines and (
        re.match(r"(?i)^(отправь сам\.?|match notes|_тип)", lines[-1].strip())
        or not lines[-1].strip()
    ):
        lines.pop()
    out = "\n".join(lines).strip()
    out = re.sub(r"(?im)^\s*отправь сам\.?\s*$", "", out).strip()
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


def format_cover_body(result: dict[str, Any]) -> str:
    """Plain cover text only — ready to copy into TG/HH."""
    return (result.get("draft") or {}).get("body") or ""


def format_cover_meta(result: dict[str, Any]) -> str:
    """Optional second message: channel / engine / fit notes. Never mixed into body."""
    draft = result["draft"]
    payload: VacancyPayload = result["payload"]
    req: CoverRequest = result["request"]
    channel_label = {
        "hh": "HH/Habr",
        "tg": "Telegram",
        "email": "email",
    }.get(draft.get("channel") or req.channel, req.channel)
    lead_bit = f"#{payload.lead_id} · " if payload.lead_id else ""
    company = (draft.get("company") or "").strip()
    title = (draft.get("title") or "").strip()
    # Guard against accidental JD dump in meta fields
    if len(company) > 80:
        company = company[:77] + "…"
    if len(title) > 100:
        title = title[:97] + "…"
    lines = [
        f"meta: {lead_bit}{company or '—'} / {title or '—'}",
        f"канал {channel_label} · {result.get('engine')}",
    ]
    if payload.url:
        lines.append(payload.url)
    if draft.get("subject"):
        lines.append(f"тема: {draft['subject']}")
    return "\n".join(lines)


def format_cover_reply(result: dict[str, Any]) -> str:
    """Backward-compatible single blob (tests / buttons). Prefer split send in bot."""
    body = format_cover_body(result)
    if result.get("raw_only", True):
        return body
    return body + "\n\n" + format_cover_meta(result)
