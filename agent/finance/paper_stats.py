"""Paper trade summaries from finance_log."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from orchestrator.state import get_conn


def paper_trade_stats(limit: int = 100) -> dict[str, Any]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT ts, payload
            FROM finance_log
            WHERE action = 'paper_trade'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    trades: list[dict[str, Any]] = []
    total_usd = 0.0
    by_side: dict[str, int] = defaultdict(int)

    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:
            continue
        size = float(payload.get("size_usd", 0))
        side = str(payload.get("side", "buy")).lower()
        total_usd += size
        by_side[side] += 1
        trades.append(
            {
                "ts": row["ts"],
                "market_id": payload.get("market_id", ""),
                "market_title": payload.get("market_title", ""),
                "side": side,
                "size_usd": size,
                "reason": payload.get("reason", ""),
            }
        )

    return {
        "count": len(trades),
        "total_usd": round(total_usd, 2),
        "by_side": dict(by_side),
        "recent": trades[:5],
    }


def format_paper_stats() -> str:
    stats = paper_trade_stats()
    if stats["count"] == 0:
        return "Paper trades: none logged yet."

    lines = [
        f"Paper trades: {stats['count']} (${stats['total_usd']:,.2f} total)",
    ]
    if stats["by_side"]:
        side_parts = [f"{k}={v}" for k, v in sorted(stats["by_side"].items())]
        lines.append(f"Sides: {', '.join(side_parts)}")

    for t in stats["recent"]:
        title = t.get("market_title") or t["market_id"][:12]
        if len(title) > 48:
            title = title[:45] + "..."
        lines.append(
            f"• {t['side']} ${t['size_usd']:.0f} — {title}"
        )
    return "\n".join(lines)
