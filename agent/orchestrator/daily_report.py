"""Format daily cycle report for Telegram Rich Messages."""

from __future__ import annotations

from typing import Any

from orchestrator.format_ru import run_status_ru
from orchestrator.health import HealthSnapshot, format_health


def format_finance_section(fin_summary: dict[str, Any]) -> str:
    """Human-readable multi-venue scan summary for daily Finance block."""
    if not fin_summary:
        return "—"

    lines: list[str] = []

    venues = fin_summary.get("venues") or []
    if venues:
        lines.append(f"**Площадки:** {', '.join(venues)}")

    for h in fin_summary.get("venue_health") or []:
        ok = h.get("ok")
        status = "OK" if ok else "ОШИБКА"
        detail = h.get("detail", "")
        lines.append(f"- `{h.get('venue', '?')}`: {status} — {detail}")

    by_venue = fin_summary.get("scan_by_venue") or {}
    if by_venue:
        parts = [f"{k}={v}" for k, v in sorted(by_venue.items())]
        total = fin_summary.get("markets_scanned", sum(by_venue.values()))
        lines.append(f"**Просканировано:** {', '.join(parts)} (всего {total})")

    after = fin_summary.get("markets_after_filters")
    rejected = fin_summary.get("markets_rejected")
    if after is not None:
        lines.append(f"**После фильтров:** {after} подходят, {rejected or 0} отсеяно")

    for sample in (fin_summary.get("rejection_samples") or [])[:2]:
        title = sample.get("title") or sample.get("market_title") or sample.get("id", "?")
        reasons = sample.get("reject_reasons") or []
        if len(title) > 40:
            title = title[:37] + "..."
        lines.append(f"  ↳ пропуск `{title}`: {'; '.join(reasons)}")

    proposals = fin_summary.get("proposals") or []
    lines.append(f"**Предложения:** {len(proposals)}")
    for p in proposals[:3]:
        venue = p.get("venue", "?")
        title = p.get("market_title") or "?"
        if len(title) > 44:
            title = title[:41] + "..."
        lines.append(f"  • [{venue}] {title} — {p.get('decision', '?')}")

    milestone = fin_summary.get("milestone") or {}
    goal = fin_summary.get("goal") or {}
    if milestone or goal:
        m_pct = milestone.get("progress_pct")
        g_pct = goal.get("progress_pct")
        parts = []
        if m_pct is not None:
            parts.append(f"M1 {m_pct:.0f}%")
        if g_pct is not None:
            parts.append(f"годовая цель {g_pct:.0f}%")
        if parts:
            lines.append(f"**Цели:** {', '.join(parts)}")

    return "\n".join(lines) if lines else "—"


def _format_job_hunt_section(job_summary: dict[str, Any] | None) -> str:
    if not job_summary:
        return "Отключено или не запускалось."
    if not job_summary.get("enabled", True):
        return "Отключено (`JOBHUNT_ENABLED=false`)."
    if job_summary.get("error"):
        return f"Ошибка скана: {job_summary['error']}"

    lines = [
        f"Новых лидов: **{job_summary.get('new_count', 0)}** "
        f"(просмотрено {job_summary.get('fetched', 0)})",
    ]
    top = job_summary.get("top_leads") or []
    if top:
        lines.append("")
        lines.append("**Топ совпадения:**")
        for lead in top[:3]:
            title = lead.get("title", "—")
            if len(title) > 50:
                title = title[:47] + "..."
            company = lead.get("company") or "—"
            lines.append(
                f"- #{lead.get('id')} **{title}** ({company}) — score {lead.get('score', 0)}"
            )
    else:
        lines.append("")
        lines.append("_Новых совпадений выше порога нет._")
    lines.append("")
    lines.append("Подробнее: `/jobs`")
    return "\n".join(lines)


def _format_bounty_section(bounty_summary: dict[str, Any] | None) -> str:
    if not bounty_summary:
        return "—"
    if bounty_summary.get("skipped_reason") == "disabled":
        return "Отключено (`BOUNTY_ENABLED=false`)."

    lines: list[str] = []
    purged = bounty_summary.get("purged_ids") or []
    if purged:
        lines.append(f"**Отсеяно:** {', '.join(f'#{i}' for i in purged)}")

    tried = bounty_summary.get("programs_tried") or []
    if tried:
        lines.append(f"**Программы:** {', '.join(tried)}")
    elif bounty_summary.get("researched_program"):
        lines.append(f"**Программа:** {bounty_summary['researched_program']}")

    if bounty_summary.get("finding_found"):
        ids = bounty_summary.get("draft_ids") or []
        lines.append(f"**Submit-ready:** #{', #'.join(str(i) for i in ids)}")
    elif bounty_summary.get("skipped_reason"):
        lines.append(f"_{bounty_summary.get('message') or 'Пропущено'}_")
    else:
        lines.append("_Submit-ready finding не найден после deep research._")

    for line in (bounty_summary.get("research_log") or [])[-4:]:
        lines.append(f"- {line}")

    lines.append("`/bounty` → `/approve bounty <id>`")
    return "\n".join(lines)


def format_daily_report_rich(
    *,
    health: HealthSnapshot,
    summary: str,
    fin_summary: dict[str, Any],
    bounty_summary: dict[str, Any] | None = None,
    job_summary: dict[str, Any] | None = None,
    commit_report: str,
    status: str = "finished",
) -> str:
    finance_block = format_finance_section(fin_summary)
    bounty_block = _format_bounty_section(bounty_summary)
    job_block = _format_job_hunt_section(job_summary)
    return f"""# Ежедневный отчёт

**Статус:** {run_status_ru(status)}

## Сервер

{format_health(health)}

## Агент

{summary.strip() or "—"}

## Финансы

{finance_block}

## Баг-баунти

{bounty_block}

## Поиск работы

{job_block}

## Git

{commit_report.strip() or "—"}
"""
