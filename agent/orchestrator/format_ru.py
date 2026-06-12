"""Russian formatting helpers for Telegram status output."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")

MONTHS_RU = (
    "янв",
    "фев",
    "мар",
    "апр",
    "май",
    "июн",
    "июл",
    "авг",
    "сен",
    "окт",
    "ноя",
    "дек",
)

RUN_STATUS_RU = {
    "finished": "завершён",
    "error": "ошибка",
    "running": "выполняется",
    "skipped": "пропущен",
}


def run_status_ru(status: str) -> str:
    return RUN_STATUS_RU.get(status, status)


def format_load(load_avg: tuple[float, float, float]) -> str:
    one, five, fifteen = load_avg
    return f"{one:.2f} / {five:.2f} / {fifteen:.2f} (1/5/15 мин)"


def format_usd(amount: float) -> str:
    rounded = round(amount, 2)
    if abs(rounded) < 0.005:
        return "$0"
    if rounded == round(rounded):
        return f"${int(round(rounded)):,}"
    return f"${rounded:,.2f}"


def format_percent(value: float) -> str:
    rounded = round(value, 1)
    if rounded == round(rounded):
        return f"{int(rounded)}%"
    return f"{rounded:.1f}%"


def format_datetime_ru(iso_ts: str, *, tz: ZoneInfo = MSK) -> str:
    dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone(tz)
    month = MONTHS_RU[local.month - 1]
    tz_label = "МСК" if tz == MSK else "UTC"
    return f"{local.day} {month}, {local.hour:02d}:{local.minute:02d} {tz_label}"


def format_date_ru(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {MONTHS_RU[dt.month - 1]} {dt.year}"


def format_last_run(ts: str, status: str, summary: str | None, *, preview_len: int = 80) -> str:
    when = format_datetime_ru(ts)
    status_ru = run_status_ru(status)
    text = (summary or "—").strip()
    if preview_len > 0 and len(text) > preview_len:
        text = text[: preview_len - 1] + "…"
    return f"{when} — {status_ru}: {text}"
