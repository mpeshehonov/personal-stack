"""Format daily cycle report for Telegram Rich Messages."""

from __future__ import annotations

from typing import Any

from orchestrator.format_ru import run_status_ru
from orchestrator.health import HealthSnapshot, format_health


def format_finance_section(fin_summary: dict[str, Any]) -> str:
    if fin_summary.get("skipped"):
        return "Paused (career hunter). FINANCE_DAILY_SCAN=false."
    if not fin_summary:
        return "—"
    return "Paused."


def _format_job_hunt_section(job_summary: dict[str, Any] | None) -> str:
    if not job_summary:
        return "Отключено или не запускалось."
    if not job_summary.get("enabled", True):
        return "Отключено (JOBHUNT_ENABLED=false)."
    if job_summary.get("error"):
        return f"Ошибка скана: {job_summary['error']}"

    lines = [
        f"Новых лидов: {job_summary.get('new_count', 0)} "
        f"(просмотрено {job_summary.get('fetched', 0)})",
    ]
    top = job_summary.get("top_leads") or []
    if top:
        lines.append("")
        lines.append("Топ совпадения (match_score):")
        for lead in top[:5]:
            title = lead.get("title", "—")
            if len(title) > 50:
                title = title[:47] + "..."
            company = lead.get("company") or "—"
            lines.append(
                f"- #{lead.get('id')} {title} ({company}) — score {lead.get('score', 0)}"
            )
    else:
        lines.append("")
        lines.append("Новых совпадений выше порога нет.")

    snippet = job_summary.get("sources_snippet")
    if snippet and snippet != "—":
        lines.append("")
        lines.append("Источники:")
        lines.append(snippet)

    ideas = (job_summary.get("opportunity") or {}).get("ideas") or []
    if ideas:
        lines.append("")
        lines.append("Opportunity ideas:")
        for title in ideas[:2]:
            lines.append(f"- {title}")

    clients_n = (job_summary.get("opportunity") or {}).get("client_orders")
    client_titles = (job_summary.get("opportunity") or {}).get("client_titles") or []
    if clients_n is not None:
        lines.append("")
        lines.append(f"Заказы (CLIENT): {clients_n}")
        for t in client_titles[:4]:
            lines.append(f"- {t}")

    morning = job_summary.get("morning_digest")
    if morning:
        lines.append("")
        lines.append("Утренний дайджест отправлен отдельным сообщением.")

    lines.append("")
    lines.append("Карточки: /jobs · /clients · /brief")
    return "\n".join(lines)


def _format_bounty_section(bounty_summary: dict[str, Any] | None) -> str:
    if not bounty_summary:
        return "—"
    if bounty_summary.get("skipped_reason") == "disabled":
        return "Paused (career hunter)."
    return "Paused."


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
    job_block = _format_job_hunt_section(job_summary)
    return f"""# Ежедневный отчёт

**Статус:** {run_status_ru(status)}

## Сервер

{format_health(health)}

## Агент

{summary.strip() or "—"}

## Поиск работы

{job_block}

## Git

{commit_report.strip() or "—"}
"""
