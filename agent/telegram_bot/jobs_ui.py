"""Telegram UX for job leads: cards + inline buttons (no typed ids)."""

from __future__ import annotations

import re
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from job_hunt.company_research import pick_open_url
from job_hunt.config import JOBHUNT_MIN_MATCH
from orchestrator.state import get_job_lead, list_job_leads


MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Вакансии", "Заказы"],
        ["Brief", "Обновить"],
        ["Скан вакансий", "Скан заказов"],
        ["Понравилось", "Справка"],
    ],
    resize_keyboard=True,
)

MENU_TEXTS = {
    "вакансии": "jobs",
    "заказы": "clients",
    "brief": "brief",
    "обновить": "refresh",
    "актуализировать": "refresh",
    "скан": "scan",
    "скан вакансий": "scan",
    "скан заказов": "client_scan",
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


def _compact_apply_hint(hint: str) -> str:
    """Shorten long URLs in card text; keep the instruction readable."""
    hint = (hint or "").strip()
    if not hint:
        return ""

    def _short_url(m: re.Match[str]) -> str:
        from urllib.parse import urlparse

        host = (urlparse(m.group(0)).netloc or "").lower()
        if not host:
            return "ссылка"
        host = host.removeprefix("www.")
        return host

    return re.sub(r"https?://[^\s<>\"']+", _short_url, hint)


def _human_source(source: str) -> str:
    s = (source or "").strip()
    if s.startswith("tg:"):
        return "Telegram · " + s[3:]
    mapping = {
        "hh": "HH",
        "habr": "Habr",
        "hirehi": "HireHi",
        "hirify": "Hirify",
        "telegram": "Telegram",
    }
    return mapping.get(s.lower(), s)


def _entity_label(entity: str) -> str:
    e = (entity or "").strip()
    if not e or e == "-":
        return "—"
    low = e.lower()
    if low in ("kwork", "kwork.ru"):
        return "Kwork"
    if low in ("fl.ru", "fl"):
        return "FL.ru"
    if low.startswith("tg/") or low.startswith("tg:"):
        ch = e.split("/", 1)[-1].split(":", 1)[-1]
        return f"Telegram · {ch}"
    return e


def lead_card_text(row: Any) -> str:
    title = row["title"] or "—"
    company = row["company"] or ""
    score = row["match_score"]
    source = row["source"] or ""
    loc = row["location"] or ""

    analysis: dict[str, Any] = {}
    overall = ""
    try:
        from opportunity.repository import get_opportunity_by_lead

        opp = get_opportunity_by_lead(int(row["id"]))
        if opp:
            overall = f" · {opp.overall_score}"
            analysis = dict(opp.analysis or {})
            if not company:
                company = analysis.get("company") or ""
    except Exception:
        pass

    company = company or "—"
    aggregator = bool(analysis.get("aggregator"))
    badge = " · радар" if aggregator else ""

    lines = [
        f"#{row['id']} · {company}{overall}{badge}",
        title,
    ]
    meta_bits = [_human_source(source)]
    if loc:
        meta_bits.append(loc)
    meta_bits.append(f"match {score}")
    lines.append(" · ".join(meta_bits))

    hint = _compact_apply_hint((analysis.get("apply_hint_ru") or "").strip())
    open_url = pick_open_url(source_url=row["url"] or "", analysis=analysis)
    if hint:
        lines.append(f"Как откликнуться: {hint}")
    elif open_url:
        lines.append("Как откликнуться: кнопка ниже")
    elif aggregator:
        lines.append("Как откликнуться: прямого контакта нет — только текст поста")
    else:
        lines.append("Как откликнуться: прямого контакта нет")
    return "\n".join(lines)


def _apply_url_rows(
    *,
    open_url: str,
    analysis: dict[str, Any] | None = None,
    buttons: dict[str, Any] | None = None,
    source_url: str = "",
) -> list[list[InlineKeyboardButton]]:
    """Build URL button rows: direct apply / source post only — never Google stubs."""
    from job_hunt.company_research import is_google_search_url

    analysis = analysis or {}
    buttons = buttons or {}
    research = analysis.get("research") or {}
    rows: list[list[InlineKeyboardButton]] = []

    primary = open_url or pick_open_url(source_url=source_url, analysis=analysis)
    if primary and is_google_search_url(primary):
        primary = ""

    hh = buttons.get("hh_url") or research.get("hh_vacancy_url") or research.get(
        "hh_employer_url"
    ) or ""
    if hh and is_google_search_url(hh):
        hh = ""

    aggregator = bool(buttons.get("aggregator") or analysis.get("aggregator"))

    if primary:
        label = "Открыть"
        low = primary.lower()
        if "hh.ru/vacancy" in low:
            label = "Отклик на HH"
        elif "hh.ru/employer" in low:
            label = "Компания на HH"
        elif "hh.ru/search" in low:
            label = "Поиск на HH"
        elif "fl.ru" in low:
            label = "Открыть на FL"
        elif "kwork.ru" in low:
            label = "Открыть на Kwork"
        elif "t.me/" in low:
            label = "Открыть пост"
        elif aggregator:
            label = "Исходный пост"
        rows.append([InlineKeyboardButton(label, url=primary)])
    elif source_url and not is_google_search_url(source_url) and "t.me/" in source_url.lower():
        rows.append([InlineKeyboardButton("Открыть пост", url=source_url)])

    secondary: list[InlineKeyboardButton] = []
    if hh and hh != primary:
        secondary.append(InlineKeyboardButton("HH", url=hh))
    # No Google «Карьера/HR поиск» stubs — either we have a real link or we don't
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
    rows = _apply_url_rows(
        open_url=open_url, analysis=analysis, source_url=url
    )
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
    # `url` here is already pick_open_url result from brief (may be empty)
    source = ""
    if lead_id:
        lead = get_job_lead(int(lead_id))
        source = (lead or {}).get("url") or ""
    open_url = url or pick_open_url(source_url=source, analysis=analysis)
    rows = _apply_url_rows(
        open_url=open_url,
        analysis=analysis,
        buttons=buttons,
        source_url=source,
    )
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
                InlineKeyboardButton("Заказы", callback_data="o:more"),
            ],
            [
                InlineKeyboardButton("Скан вакансий", callback_data="j:scan"),
                InlineKeyboardButton("Скан заказов", callback_data="o:scan"),
            ],
            [
                InlineKeyboardButton("Обновить статусы", callback_data="o:refresh"),
            ],
        ]
    )


def brief_vertical_keyboard(opp_id: int, url: str = "") -> InlineKeyboardMarkup:
    """Backward-compatible alias — same as client order keyboard."""
    return client_keyboard(opp_id, url)


def client_card_text(opp: Any) -> str:
    analysis = dict(getattr(opp, "analysis", None) or {})
    kind = analysis.get("kind") or ""
    price = analysis.get("price") or ""
    why = list((getattr(opp, "scores", None) or {}).get("fit", {}).get("reasons") or [])[:2]
    if not why:
        why = list(analysis.get("why") or [])[:2]
    kind_ru = {
        "freelance_order": "заказ",
        "retainer": "ретейнер",
        "target": "цель",
    }.get(str(kind), str(kind) or "заказ")
    title = (opp.title or "—").removeprefix("Заказ: ").strip() or "—"
    lines = [
        f"#{opp.id} · {_entity_label(opp.company_or_entity)} · {opp.overall_score}",
        title,
        kind_ru,
    ]
    if price:
        lines.append(str(price)[:80])
    hint = ""
    try:
        from opportunity.actions import action_how_ru

        hint = action_how_ru(opp.next_action, analysis)
    except Exception:
        hint = ""
    if hint:
        lines.append(f"Что сделать: {hint}")
    # Keep only human-useful why bits (freshness / stack), skip noise
    useful = []
    for item in why:
        s = str(item).strip()
        if not s:
            continue
        if s.startswith("стек:") or "опубликовано" in s or "смежно" in s:
            useful.append(s)
    if useful:
        lines.append(" · ".join(useful[:2]))
    return "\n".join(lines)


def client_keyboard(opp_id: int, url: str = "") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if url and "t.me/runello" not in url.lower() and "gmatch" not in url.lower():
        rows.append([InlineKeyboardButton("Открыть заказ", url=url)])
    rows.append(
        [
            InlineKeyboardButton("Ок", callback_data=f"o:like:{opp_id}"),
            InlineKeyboardButton("Мимо", callback_data=f"o:pass:{opp_id}"),
            InlineKeyboardButton("Откликнулся", callback_data=f"o:done:{opp_id}"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("Ещё заказы", callback_data="o:more"),
            InlineKeyboardButton("Скан заказов", callback_data="o:scan"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("Обновить статусы", callback_data="o:refresh"),
        ]
    )
    return InlineKeyboardMarkup(rows)


def clients_intro(count: int) -> str:
    if count <= 0:
        return (
            "Живых заказов сейчас нет.\n"
            "Жми «Скан заказов» или «Обновить»."
        )
    return (
        f"Заказов: {count} (показываю до 5).\n"
        "Открыть → Ок / Мимо / Откликнулся."
    )


def list_client_orders(*, liked: bool = False, limit: int = 5) -> list[Any]:
    from opportunity.models import OpportunityStatus
    from opportunity.repository import list_opportunities

    status = OpportunityStatus.SAVED.value if liked else OpportunityStatus.NEW.value
    rows = list_opportunities(
        status=status,
        opp_type="CLIENT",
        limit=40,
        min_overall=40 if not liked else 0,
    )

    def _key(o: Any) -> tuple:
        kind = (o.analysis or {}).get("kind") or ""
        rank = {"freelance_order": 0, "retainer": 1}.get(kind, 2)
        return (rank, -int(o.overall_score or 0))

    rows = sorted(rows, key=_key)
    return rows[:limit]


def parse_opp_callback(data: str) -> tuple[str, int | None]:
    parts = (data or "").split(":")
    if len(parts) < 2 or parts[0] != "o":
        return "", None
    action = parts[1]
    if action in ("more", "scan", "refresh", "liked"):
        return action, None
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
            f"Новых вакансий с match ≥ {JOBHUNT_MIN_MATCH} нет.\n"
            "Жми «Скан»."
        )
    return (
        f"Новых вакансий: {count} (показываю до 5).\n"
        "Ссылка отклика · Ок / Мимо / Сопровод."
    )
