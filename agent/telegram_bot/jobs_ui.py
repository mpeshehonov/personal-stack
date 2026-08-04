"""Telegram UX for job leads: cards + inline buttons (no typed ids)."""

from __future__ import annotations

import json
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from job_hunt.company_research import pick_open_url
from job_hunt.config import JOBHUNT_MIN_MATCH
from orchestrator.state import get_job_lead, list_job_leads


MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Вакансии", "Brief"],
        ["Скан", "Источники"],
        ["Понравилось", "Справка"],
    ],
    resize_keyboard=True,
)

MENU_TEXTS = {
    "вакансии": "jobs",
    "brief": "brief",
    "скан": "scan",
    "источники": "sources",
    "понравилось": "liked",
    "справка": "help",
    "меню": "menu",
}


def parse_menu_text(text: str) -> str | None:
    key = (text or "").strip().lower()
    return MENU_TEXTS.get(key)


def _analysis_for_lead(lead_id: int) -> dict[str, Any]:
    try:
        from opportunity.repository import get_opportunity_by_lead

        opp = get_opportunity_by_lead(int(lead_id))
        if opp:
            return dict(opp.analysis or {})
    except Exception:
        pass
    return {}


def lead_card_text(row: Any) -> str:
    title = row["title"] or "-"
    company = row["company"] or "-"
    score = row["match_score"]
    source = row["source"] or ""
    loc = row["location"] or ""
    reasons = []
    try:
        reasons = json.loads(row["match_reasons_json"] or "[]")
    except json.JSONDecodeError:
        pass
    reason_line = ""
    if reasons:
        reason_line = "\n" + reasons[0]

    overall_line = ""
    analysis: dict[str, Any] = {}
    try:
        from opportunity.repository import get_opportunity_by_lead

        opp = get_opportunity_by_lead(int(row["id"]))
        if opp:
            overall_line = f" · opp {opp.overall_score}"
            analysis = dict(opp.analysis or {})
            if analysis.get("aggregator"):
                overall_line += " · радар"
            elif analysis.get("paywall"):
                overall_line += " · paywall"
            if not company or company == "-":
                company = analysis.get("company") or company
    except Exception:
        pass

    lines = [
        f"#{row['id']} · match {score}{overall_line}",
        f"{company}",
        title,
    ]
    meta = " · ".join(p for p in (source, loc) if p)
    if meta:
        lines.append(meta)
    if reason_line:
        lines.append(reason_line.strip())
    hint = (analysis.get("apply_hint_ru") or "").strip()
    if hint:
        lines.append(f"Отклик: {hint}")
    return "\n".join(lines)


def _apply_url_rows(
    *,
    open_url: str,
    analysis: dict[str, Any] | None = None,
    buttons: dict[str, Any] | None = None,
) -> list[list[InlineKeyboardButton]]:
    """Build URL button rows: direct apply first, never Runello-bot as primary."""
    analysis = analysis or {}
    buttons = buttons or {}
    research = analysis.get("research") or {}
    rows: list[list[InlineKeyboardButton]] = []

    primary = open_url or pick_open_url(source_url="", analysis=analysis)
    hh = (
        buttons.get("hh_url")
        or research.get("hh_vacancy_url")
        or research.get("hh_employer_url")
        or ""
    )
    career = buttons.get("career_url") or research.get("career_search_url") or ""
    hr = (
        buttons.get("hr_url")
        or research.get("tg_hr_search_url")
        or research.get("linkedin_search_url")
        or ""
    )
    aggregator = bool(buttons.get("aggregator") or analysis.get("aggregator"))

    if primary:
        label = "Прямой отклик"
        if "hh.ru/vacancy" in primary:
            label = "Отклик на HH"
        elif "hh.ru/employer" in primary or "hh.ru/search" in primary:
            label = "Искать на HH"
        elif "google.com/search" in primary:
            label = "Найти карьеру/HR"
        elif aggregator:
            label = "Искать прямой контакт"
        rows.append([InlineKeyboardButton(label, url=primary)])

    secondary: list[InlineKeyboardButton] = []
    if hh and hh != primary:
        secondary.append(
            InlineKeyboardButton(
                "HH",
                url=hh,
            )
        )
    if career and career != primary and career != hh:
        secondary.append(InlineKeyboardButton("Карьера", url=career))
    if hr and hr not in (primary, hh, career):
        secondary.append(InlineKeyboardButton("HR поиск", url=hr))
    if secondary:
        rows.append(secondary[:3])
    return rows


def lead_keyboard(
    lead_id: int,
    url: str = "",
    *,
    analysis: dict[str, Any] | None = None,
) -> InlineKeyboardMarkup:
    analysis = analysis if analysis is not None else _analysis_for_lead(lead_id)
    open_url = pick_open_url(source_url=url, analysis=analysis)
    rows = _apply_url_rows(open_url=open_url, analysis=analysis)
    rows.append(
        [
            InlineKeyboardButton("Ок", callback_data=f"j:like:{lead_id}"),
            InlineKeyboardButton("Мимо", callback_data=f"j:pass:{lead_id}"),
            InlineKeyboardButton("Сопровод", callback_data=f"j:cover:{lead_id}"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("Откликнулся", callback_data=f"j:applied:{lead_id}"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("Ещё вакансии", callback_data="j:more"),
            InlineKeyboardButton("Скан", callback_data="j:scan"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def brief_lead_keyboard(
    lead_id: int,
    url: str = "",
    *,
    analysis: dict[str, Any] | None = None,
    buttons: dict[str, Any] | None = None,
) -> InlineKeyboardMarkup:
    """Compact keyboard under each brief card."""
    analysis = analysis if analysis is not None else _analysis_for_lead(lead_id)
    open_url = url or pick_open_url(source_url="", analysis=analysis)
    rows = _apply_url_rows(open_url=open_url, analysis=analysis, buttons=buttons)
    rows.append(
        [
            InlineKeyboardButton("Откликнулся", callback_data=f"j:applied:{lead_id}"),
            InlineKeyboardButton("В избранное", callback_data=f"j:like:{lead_id}"),
            InlineKeyboardButton("Мимо", callback_data=f"j:pass:{lead_id}"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("Сопровод", callback_data=f"j:cover:{lead_id}"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def brief_nav_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Вакансии", callback_data="j:more"),
                InlineKeyboardButton("Скан", callback_data="j:scan"),
            ]
        ]
    )


def brief_vertical_keyboard(opp_id: int, url: str = "") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if url and "t.me/runello" not in url.lower() and "gmatch" not in url.lower():
        rows.append([InlineKeyboardButton("Открыть", url=url)])
    rows.append(
        [
            InlineKeyboardButton("Ок", callback_data=f"o:like:{opp_id}"),
            InlineKeyboardButton("Сделано", callback_data=f"o:done:{opp_id}"),
            InlineKeyboardButton("Мимо", callback_data=f"o:pass:{opp_id}"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def parse_opp_callback(data: str) -> tuple[str, int | None]:
    parts = (data or "").split(":")
    if len(parts) < 2 or parts[0] != "o":
        return "", None
    action = parts[1]
    if len(parts) >= 3 and parts[2].isdigit():
        return action, int(parts[2])
    return action, None


def sources_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Вакансии", callback_data="j:more"),
                InlineKeyboardButton("Скан", callback_data="j:scan"),
            ]
        ]
    )


def parse_job_callback(data: str) -> tuple[str, int | None]:
    """Return (action, lead_id|None)."""
    parts = (data or "").split(":")
    if len(parts) < 2 or parts[0] != "j":
        return "", None
    action = parts[1]
    if action in ("more", "scan"):
        return action, None
    if len(parts) >= 3 and parts[2].isdigit():
        return action, int(parts[2])
    return action, None


def list_new_leads(limit: int = 5) -> list[Any]:
    return list_job_leads(status="new", limit=limit, min_score=JOBHUNT_MIN_MATCH)


def list_liked_leads(limit: int = 10) -> list[Any]:
    return list_job_leads(status="liked", limit=limit, min_score=0)


def get_lead(lead_id: int) -> Any | None:
    return get_job_lead(lead_id)


def jobs_intro(count: int) -> str:
    if count <= 0:
        return (
            f"Новых вакансий с score ≥ {JOBHUNT_MIN_MATCH} нет.\n"
            "Нажми «Скан» или кнопку ниже."
        )
    return (
        f"Новых вакансий: {count} (показываю до 5).\n"
        "Кнопки: прямой отклик/HH (не бот агрегатора) · Ок / Мимо / Сопровод."
    )
