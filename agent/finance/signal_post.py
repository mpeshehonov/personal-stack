"""Format and post top scan hits to a Telegram signals channel (A3 lane)."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

from orchestrator.config import load_env_file

logger = logging.getLogger(__name__)


def _market_label(market: dict[str, Any]) -> str:
    for key in ("title", "question", "market_title", "description"):
        val = market.get(key)
        if val:
            return str(val)
    mid = market.get("condition_id") or market.get("id") or "?"
    return str(mid)


def _market_detail(market: dict[str, Any]) -> str:
    parts: list[str] = []
    if market.get("last_price") is not None:
        parts.append(f"price {market['last_price']}")
    if market.get("edge_pct") is not None:
        parts.append(f"edge {float(market['edge_pct']):.1f}%")
    if market.get("turnover") is not None:
        parts.append(f"turnover ${float(market['turnover']):,.0f}")
    change = market.get("change_24h_pct")
    if change is None and market.get("bybit"):
        change = market["bybit"].get("change_24h_pct")
    if change is not None:
        try:
            parts.append(f"24h {float(change) * 100:+.2f}%")
        except (TypeError, ValueError):
            pass
    return " · ".join(parts) if parts else "—"


def format_top_scan_markdown(
    fin_summary: dict[str, Any],
    *,
    top_n: int = 3,
    locale: str = "ru",
) -> str:
    """Structured markdown for Telegram — header + top N tradeable markets."""
    tradeable = fin_summary.get("tradeable_markets") or []
    proposals = fin_summary.get("proposals") or []
    by_venue = fin_summary.get("scan_by_venue") or {}
    after = fin_summary.get("markets_after_filters", len(tradeable))
    scanned = fin_summary.get("markets_scanned", sum(by_venue.values()))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if locale == "en":
        header = f"**Scan signals** · {ts}\nScanned **{scanned}** → **{after}** tradeable"
    else:
        header = f"**Сигналы скана** · {ts}\nПросканировано **{scanned}** → **{after}** подходят"

    if by_venue:
        venue_line = ", ".join(f"{k}={v}" for k, v in sorted(by_venue.items()))
        header += f"\n`{venue_line}`"

    lines = [header, ""]

    picks: list[dict[str, Any]] = list(tradeable[:top_n])
    if not picks and proposals:
        for p in proposals[:top_n]:
            prop = p.get("proposal") or {}
            picks.append(
                {
                    "venue": p.get("venue") or prop.get("venue") or "?",
                    "title": p.get("market_title") or prop.get("market_id", "?"),
                    "condition_id": prop.get("market_id"),
                }
            )

    if not picks:
        empty = "No tradeable markets today." if locale == "en" else "Сегодня нет подходящих рынков."
        return f"{header}\n\n_{empty}_"

    for i, market in enumerate(picks, 1):
        venue = market.get("venue") or "?"
        title = _market_label(market)
        if len(title) > 56:
            title = title[:53] + "..."
        detail = _market_detail(market)
        lines.append(f"**{i}. [{venue}]** {title}")
        lines.append(f"   {detail}")
        lines.append("")

    footer = (
        "_Paper mode — not financial advice._"
        if locale == "en"
        else "_Paper mode — не финансовый совет._"
    )
    lines.append(footer)
    return "\n".join(lines).strip()


def post_scan_to_channel(markdown: str) -> dict[str, Any]:
    """Post markdown to TELEGRAM_SIGNAL_CHANNEL_ID. No-op if not configured."""
    load_env_file(".env.telegram")
    load_env_file(".env.finance")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel = os.environ.get("TELEGRAM_SIGNAL_CHANNEL_ID", "").strip()

    if not token or not channel:
        return {"status": "skipped", "reason": "no token or TELEGRAM_SIGNAL_CHANNEL_ID"}

    try:
        chat_id: int | str = int(channel)
    except ValueError:
        chat_id = channel

    payload = {
        "chat_id": chat_id,
        "text": markdown[:4096],
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = httpx.post(url, json=payload, timeout=30)
        data = resp.json()
        if data.get("ok"):
            return {"status": "sent", "chat_id": str(chat_id)}
        return {"status": "error", "description": data.get("description", resp.text[:200])}
    except httpx.HTTPError as e:
        logger.warning("signal channel post failed: %s", e)
        return {"status": "error", "description": str(e)}


def maybe_post_scan_signals(fin_summary: dict[str, Any]) -> dict[str, Any]:
    """Format top-3 and post when channel id is set."""
    markdown = format_top_scan_markdown(fin_summary)
    result = post_scan_to_channel(markdown)
    result["preview"] = markdown[:500]
    return result
