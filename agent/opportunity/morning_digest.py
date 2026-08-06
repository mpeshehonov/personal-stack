"""Morning digest: fresh jobs + client orders for Telegram."""

from __future__ import annotations

from typing import Any


def build_morning_digest(*, jobs_n: int = 5, clients_n: int = 5) -> dict[str, Any]:
    """Collect top open jobs/orders after ensuring scans ran elsewhere."""
    from telegram_bot.jobs_ui import (
        client_card_text,
        lead_card_text,
        list_client_orders,
        list_new_leads,
    )

    jobs = list_new_leads(limit=jobs_n)
    clients = list_client_orders(limit=clients_n)
    job_cards = [lead_card_text(r) for r in jobs]
    client_cards = [client_card_text(o) for o in clients]
    return {
        "jobs_count": len(jobs),
        "clients_count": len(clients),
        "job_cards": job_cards,
        "client_cards": client_cards,
        "jobs": jobs,
        "clients": clients,
    }


def format_morning_digest_markdown(
    digest: dict[str, Any] | None = None,
    *,
    scan_stats: dict[str, Any] | None = None,
) -> str:
    digest = digest or build_morning_digest()
    scan_stats = scan_stats or {}
    lines = [
        "# Утренний дайджест",
        "",
        f"Вакансии: {digest.get('jobs_count', 0)} · Заказы: {digest.get('clients_count', 0)}",
    ]
    if scan_stats:
        js = scan_stats.get("job_scan") or {}
        cs = scan_stats.get("client_scan") or {}
        arch = scan_stats.get("archived_total")
        bits = []
        if js.get("new_count") is not None:
            bits.append(f"новых вакансий {js.get('new_count')}")
        if cs.get("upserted") is not None:
            bits.append(f"заказов в базу {cs.get('upserted')}")
        if arch is not None:
            bits.append(f"снято закрытых {arch}")
        if bits:
            lines.append("Скан: " + ", ".join(bits))

    lines.append("")
    lines.append("## Вакансии")
    job_cards = digest.get("job_cards") or []
    if not job_cards:
        lines.append("Пока пусто — жми «Скан вакансий».")
    else:
        for card in job_cards:
            lines.append("")
            lines.append(card)

    lines.append("")
    lines.append("## Заказы")
    client_cards = digest.get("client_cards") or []
    if not client_cards:
        lines.append("Живых заказов нет — жми «Скан заказов».")
    else:
        for card in client_cards:
            lines.append("")
            lines.append(card)

    lines.append("")
    lines.append("Карточки с кнопками: /jobs · /clients · полный /brief")
    return "\n".join(lines)


def run_morning_pipeline(*, rescan: bool = True) -> dict[str, Any]:
    """Refresh (+ optional rescan) then build digest payload."""
    from opportunity.refresh_open import refresh_open_pipeline

    stats = refresh_open_pipeline(rescan=rescan)
    digest = build_morning_digest()
    return {
        "stats": stats,
        "digest": digest,
        "markdown": format_morning_digest_markdown(digest, scan_stats=stats),
    }