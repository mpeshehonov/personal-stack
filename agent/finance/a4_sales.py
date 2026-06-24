"""Log A4 (Gumroad) product sales into finance_log for M1 goal tracking."""

from __future__ import annotations

import argparse
import json
from typing import Any

from orchestrator.state import get_conn, log_finance, year_pnl

ACTION = "a4_sale"
DEFAULT_PRODUCT = "personal-stack-agent-starter"


def log_gumroad_sale(
    *,
    net_usd: float,
    order_id: str = "",
    product: str = DEFAULT_PRODUCT,
    lane: str = "A4",
    notes: str = "",
) -> dict[str, Any]:
    """Record realized net revenue from a Gumroad sale (after platform fees)."""
    payload: dict[str, Any] = {
        "lane": lane,
        "product": product,
        "order_id": order_id,
        "net_usd": net_usd,
        "notes": notes,
    }
    log_finance(ACTION, payload, pnl_usd=net_usd)
    return payload


def a4_sale_stats(year: int | None = None) -> dict[str, Any]:
    year = year or __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).year
    prefix = f"{year}-%"
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT ts, payload, pnl_usd
            FROM finance_log
            WHERE action = ? AND ts LIKE ?
            ORDER BY id DESC
            """,
            (ACTION, prefix),
        ).fetchall()

    sales: list[dict[str, Any]] = []
    total_net = 0.0
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:
            payload = {}
        net = float(row["pnl_usd"] or 0)
        total_net += net
        sales.append(
            {
                "ts": row["ts"],
                "net_usd": net,
                "order_id": payload.get("order_id", ""),
                "product": payload.get("product", DEFAULT_PRODUCT),
            }
        )

    return {
        "year": year,
        "count": len(sales),
        "total_net_usd": round(total_net, 2),
        "recent": sales[:5],
    }


def format_a4_sales() -> str:
    stats = a4_sale_stats()
    if stats["count"] == 0:
        return "A4 sales: none logged yet."
    lines = [
        f"A4 sales ({stats['year']}): {stats['count']} "
        f"(${stats['total_net_usd']:,.2f} net)",
    ]
    for s in stats["recent"]:
        oid = s.get("order_id") or "—"
        lines.append(f"• ${s['net_usd']:.2f} — {oid}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Log a Gumroad sale (lane A4) into finance_log"
    )
    parser.add_argument(
        "--net-usd",
        type=float,
        required=True,
        help="Net USD after Gumroad/payment fees (counts toward M1 PnL)",
    )
    parser.add_argument("--order-id", default="", help="Gumroad order or sale ID")
    parser.add_argument("--product", default=DEFAULT_PRODUCT)
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload without writing to finance_log",
    )
    args = parser.parse_args()

    if args.net_usd <= 0:
        raise SystemExit("net-usd must be positive")

    payload = {
        "lane": "A4",
        "product": args.product,
        "order_id": args.order_id,
        "net_usd": args.net_usd,
        "notes": args.notes,
    }
    if args.dry_run:
        print(json.dumps({"action": ACTION, "payload": payload, "pnl_usd": args.net_usd}, indent=2))
        return

    log_gumroad_sale(
        net_usd=args.net_usd,
        order_id=args.order_id,
        product=args.product,
        notes=args.notes,
    )
    earned = year_pnl()
    print(f"Logged A4 sale ${args.net_usd:.2f} (order: {args.order_id or 'n/a'})")
    print(f"Year PnL: ${earned:.2f}")


if __name__ == "__main__":
    main()
