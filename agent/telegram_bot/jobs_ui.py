"""Telegram UX for job leads: cards + inline buttons (no typed ids)."""

from __future__ import annotations

import json
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

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
    try:
        from opportunity.repository import get_opportunity_by_lead

        opp = get_opportunity_by_lead(int(row["id"]))
        if opp:
            overall_line = f" · opp {opp.overall_score}"
            if opp.analysis.get("paywall"):
                overall_line += " · paywall"
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
    return "\n".join(lines)


def lead_keyboard(lead_id: int, url: str = "") -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Ок", callback_data=f"j:like:{lead_id}"),
            InlineKeyboardButton("Мимо", callback_data=f"j:pass:{lead_id}"),
            InlineKeyboardButton("Сопровод", callback_data=f"j:cover:{lead_id}"),
        ]
    ]
    if url:
        rows.append([InlineKeyboardButton("Открыть вакансию", url=url)])
    rows.append(
        [
            InlineKeyboardButton("Ещё вакансии", callback_data="j:more"),
            InlineKeyboardButton("Скан", callback_data="j:scan"),
        ]
    )
    return InlineKeyboardMarkup(rows)


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
        "Кнопки под карточкой: Ок / Мимо / Сопровод."
    )
