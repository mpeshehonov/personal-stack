"""Cover letter drafts — rules from agent/skills/cover-letter/SKILL.md (no LLM, no send)."""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any, Literal

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT
from orchestrator.config import SITE_DIR

Channel = Literal["hh", "email"]

RESUME_JSON = SITE_DIR / "content" / "resume" / "resume.json"
RESUME_URL = "https://mpeshekhonov.ru/ru/resume"
TELEGRAM = "@makusimu_san"
PHONE = "+7 950 919-67-86"
NAME = "Максим Пешехонов"

# Named proofs — one per letter (skill: no resume dump)

_AI_CHARS = str.maketrans({
    "—": ",",
    "–": "-",
    "→": " ",
    "←": " ",
    "⇒": " ",
    "·": ",",
    "•": " ",
    "…": ".",
})
_AI_PATTERNS = [
    (re.compile(r"\s*->\s*"), " "),
    (re.compile(r"\s*=>\s*"), " "),
    (re.compile(r"\s*\|\s*"), ", "),
    (re.compile(r",\s*,+"), ","),
    (re.compile(r"\s{2,}"), " "),
]


def _validate_cyrillic_name(text: str) -> None:
    for line in text.splitlines():
        if "Пешех" in line or "Максим" in line:
            for ch in line:
                if ch.isalpha() and ord(ch) < 128:
                    raise ValueError(f"Latin letter in name line: {line!r}")


def humanize_cover_text(text: str) -> str:
    out = text.translate(_AI_CHARS)
    for pattern, repl in _AI_PATTERNS:
        out = pattern.sub(repl, out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    _validate_cyrillic_name(out)
    return out


PROOFS: dict[str, str] = {
    "ecommerce": (
        "На Citilink переносил каталог citilink.ru на Next.js и React: "
        "фильтры, URL state, SEO. Сейчас checkout PREEGLOS на Next.js с Orval."
    ),
    "enterprise": (
        "На X5 Tech делал модуль согласования закупок: React, TypeScript, "
        "Keycloak SSO, Orval по OpenAPI, длинные формы, code splitting."
    ),
    "product": (
        "На sendonate.com три React-клиента, WebSocket, Orval и CI/CD из одного репозитория."
    ),
    "bitrix": (
        "Есть опыт 1C-Bitrix и Symfony/MySQL (кейсы на сайте). "
        "Сейчас основной фокус React, TypeScript, Next.js."
    ),
    "python": (
        "Frontend-first: в POTALONU связал React с Django REST через Orval. "
        "До этого React в X5 и Citilink."
    ),
    "data": (
        "В BI.ZONE Threat Intelligence: React, GraphQL, D3-граф, виртуализация списков."
    ),
    "general": (
        "Последние роли X5 Tech и Citilink, сейчас продуктовые клиенты на React и Vite."
    ),
}

CLASSIFIERS: list[tuple[str, tuple[str, ...]]] = [
    ("bitrix", ("bitrix", "битрикс", "1c-bitrix", "cms", "symfony", "php")),
    ("ecommerce", ("e-commerce", "ecommerce", "интернет-магазин", "каталог", "checkout", "магазин")),
    ("enterprise", ("enterprise", "rbac", "keycloak", "закуп", "согласован", "corporate")),
    ("python", ("python", "django", "fastapi", "backend", "fullstack", "full-stack")),
    ("data", ("graphql", "аналит", "soc", "дашборд", "d3", "виртуализац")),
    ("product", ("mini app", "telegram", "startup", "продукт", "websocket", "real-time")),
]


def _load_resume() -> dict[str, Any]:
    if not RESUME_JSON.exists():
        return {}
    return json.loads(RESUME_JSON.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _strip_html(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def fetch_hh_vacancy_description(external_id: str) -> str:
    try:
        resp = httpx.get(
            f"https://api.hh.ru/vacancies/{external_id}",
            headers={"User-Agent": JOBHUNT_USER_AGENT},
            timeout=25,
        )
        if resp.status_code != 200:
            return ""
        desc = resp.json().get("description") or ""
        return _strip_html(desc)[:5000]
    except httpx.HTTPError:
        return ""


def vacancy_text_from_lead(lead: dict[str, Any]) -> str:
    parts = [lead.get("title") or "", lead.get("description_snippet") or ""]
    skills = lead.get("skills_json") or "[]"
    try:
        parts.extend(json.loads(skills))
    except json.JSONDecodeError:
        pass
    if lead.get("source") == "hh" and lead.get("external_id"):
        detail = fetch_hh_vacancy_description(str(lead["external_id"]))
        if detail:
            parts.append(detail)
    return _normalize(" ".join(p for p in parts if p))


def classify_vacancy(text: str) -> str:
    for kind, keywords in CLASSIFIERS:
        if any(kw in text for kw in keywords):
            return kind
    return "general"


def _jd_hook(title: str, company: str, text: str, kind: str) -> str:
    company_part = f" в {company}" if company else ""
    if kind == "ecommerce":
        return (
            f"Пишу по вакансии «{title}»{company_part}. "
            f"У вас e-commerce и React, это близко к моему опыту каталога и checkout."
        )
    if kind == "enterprise":
        return (
            f"Пишу по «{title}»{company_part}. "
            f"Enterprise UI, роли и длинные формы делал в X5 Tech."
        )
    if kind == "bitrix":
        return (
            f"Пишу по «{title}»{company_part}. "
            f"Bitrix есть в проектах, сейчас основной стек React и TypeScript."
        )
    if kind == "python":
        return (
            f"Пишу по «{title}»{company_part}. "
            f"Frontend-first, React-клиенты с Django REST backend."
        )
    if kind == "product":
        return (
            f"Пишу по «{title}»{company_part}. "
            f"Несколько клиентов на одном backend, это мой текущий профиль."
        )
    return (
        f"Пишу по «{title}»{company_part}. "
        f"React и TypeScript совпадают с моим последним опытом."
    )


def _subject_line(title: str) -> str:
    short = title[:60].strip() if title else "Frontend"
    return f"Senior Frontend, React - {NAME} / {short}"


def draft_cover_hh(lead: dict[str, Any]) -> str:
    """HH / Habr short field, ≤500 chars."""
    resume = _load_resume()
    summary = resume.get("summary", "Senior Frontend, React/TS/Next.js, 7+ лет.")
    text = vacancy_text_from_lead(lead)
    kind = classify_vacancy(text)
    proof = PROOFS[kind]
    # First sentence from summary (trim)
    line1 = summary.split(".")[0].strip()
    if len(line1) > 120:
        line1 = "Senior Frontend, 7 лет: React, TypeScript, Next.js."
    line2 = proof.split(".")[0].strip() + "."
    body = f"{line1} {line2} Удалённо, Сочи. {RESUME_URL}"
    if len(body) > 500:
        body = (
            f"Senior Frontend, 7 лет, React и TypeScript. {line2} "
            f"Удалённо, Сочи. {RESUME_URL}"
        )
    return humanize_cover_text(body[:500])


def draft_cover_email(lead: dict[str, Any]) -> str:
    """Email body ~120–180 words, skill structure."""
    title = lead.get("title") or "Frontend-разработчик"
    company = lead.get("company") or ""
    text = vacancy_text_from_lead(lead)
    kind = classify_vacancy(text)
    hook = _jd_hook(title, company, text, kind)
    proof = PROOFS[kind]
    paragraphs = [
        "Здравствуйте!",
        "",
        hook,
        "",
        proof,
        "",
        "Удалённо из Сочи, могу выйти в ближайшее время.",
        "",
        f"Резюме: {RESUME_URL}",
        f"Telegram: {TELEGRAM}",
        "",
        "С уважением,",
        NAME,
        PHONE,
    ]
    return humanize_cover_text("\n".join(paragraphs))


def draft_cover_letter(
    lead: dict[str, Any],
    *,
    channel: Channel = "hh",
) -> dict[str, str]:
    """Return structured draft for Telegram / storage."""
    title = lead.get("title") or "—"
    company = lead.get("company") or "—"
    text = vacancy_text_from_lead(lead)
    kind = classify_vacancy(text)

    if channel == "email":
        body = draft_cover_email(lead)
        subject = _subject_line(title)
    else:
        body = draft_cover_hh(lead)
        subject = ""

    return {
        "title": title,
        "company": company,
        "channel": channel,
        "subject": subject,
        "body": body,
        "hook_kind": kind,
        "url": lead.get("url") or "",
    }


def format_draft_markdown(draft: dict[str, str], *, lead_id: int) -> str:
    lines = [
        f"## Сопровод — #{lead_id}",
        "",
        f"**{draft['company']}** · {draft['title']}",
        f"**Канал:** {'email' if draft['channel'] == 'email' else 'HH/Habr (≤500 символов)'}",
    ]
    if draft.get("url"):
        lines.append(f"**Вакансия:** {draft['url']}")
    lines.append("")
    if draft.get("subject"):
        lines.extend([f"**Тема:** {draft['subject']}", ""])
    lines.extend(
        [
            "```",
            draft["body"],
            "```",
            "",
            f"_Тип: {draft['hook_kind']}. Отправь сам._",
            f"_PDF: {RESUME_URL.replace('/ru/resume', '/ru/resume/download')}_",
        ]
    )
    return "\n".join(lines)
