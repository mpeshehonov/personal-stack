"""Log accepted bug bounty rewards into finance_log for M1 goal tracking."""

from __future__ import annotations

import argparse
import json
from typing import Any

from orchestrator.state import get_conn, log_finance, year_pnl

ACTION = "bounty_payout"
LANE = "A7"
VALID_PLATFORMS = frozenset(
    {"hackerone", "immunefi", "hackenproof", "bugcrowd", "intigriti", "yeswehack", "other"}
)
VALID_PAYOUT_RAILS = frozenset({"crypto", "bank", "paypal", "unknown"})


def log_bounty_payout(
    *,
    net_usd: float,
    platform: str,
    report_id: str = "",
    program: str = "",
    payout_rail: str = "crypto",
    lane: str = LANE,
    notes: str = "",
) -> dict[str, Any]:
    """Record realized net revenue from an accepted bounty payout (after fees)."""
    platform_norm = platform.strip().lower()
    if platform_norm not in VALID_PLATFORMS:
        raise ValueError(
            f"platform must be one of {sorted(VALID_PLATFORMS)}, got {platform!r}"
        )
    rail_norm = payout_rail.strip().lower()
    if rail_norm not in VALID_PAYOUT_RAILS:
        raise ValueError(
            f"payout_rail must be one of {sorted(VALID_PAYOUT_RAILS)}, got {payout_rail!r}"
        )

    payload: dict[str, Any] = {
        "lane": lane,
        "platform": platform_norm,
        "report_id": report_id,
        "program": program,
        "payout_rail": rail_norm,
        "net_usd": net_usd,
        "notes": notes,
    }
    log_finance(ACTION, payload, pnl_usd=net_usd)
    return payload


def bounty_payout_stats(year: int | None = None) -> dict[str, Any]:
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

    payouts: list[dict[str, Any]] = []
    total_net = 0.0
    by_platform: dict[str, float] = {}
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except json.JSONDecodeError:
            payload = {}
        net = float(row["pnl_usd"] or 0)
        total_net += net
        platform = payload.get("platform", "other")
        by_platform[platform] = by_platform.get(platform, 0.0) + net
        payouts.append(
            {
                "ts": row["ts"],
                "net_usd": net,
                "platform": platform,
                "report_id": payload.get("report_id", ""),
                "program": payload.get("program", ""),
                "payout_rail": payload.get("payout_rail", "unknown"),
            }
        )

    return {
        "year": year,
        "count": len(payouts),
        "total_net_usd": round(total_net, 2),
        "by_platform": {k: round(v, 2) for k, v in sorted(by_platform.items())},
        "recent": payouts[:5],
    }


def format_bounty_payouts() -> str:
    stats = bounty_payout_stats()
    if stats["count"] == 0:
        return "Bounty payouts: none logged yet."
    lines = [
        f"Bounty payouts ({stats['year']}): {stats['count']} "
        f"(${stats['total_net_usd']:,.2f} net)",
    ]
    for s in stats["recent"]:
        rid = s.get("report_id") or "—"
        prog = s.get("program") or s.get("platform", "")
        lines.append(f"• ${s['net_usd']:.2f} — {prog} ({rid})")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Log an accepted bug bounty payout into finance_log"
    )
    parser.add_argument(
        "--net-usd",
        type=float,
        help="Net USD after platform fees (counts toward M1 PnL)",
    )
    parser.add_argument(
        "--platform",
        choices=sorted(VALID_PLATFORMS),
        help="Bounty platform (e.g. immunefi, hackerone)",
    )
    parser.add_argument("--report-id", default="", help="Platform report/finding ID")
    parser.add_argument("--program", default="", help="Program or team name")
    parser.add_argument(
        "--payout-rail",
        default="crypto",
        choices=sorted(VALID_PAYOUT_RAILS),
        help="How payout was received (default: crypto)",
    )
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload without writing to finance_log",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show logged bounty payout stats and exit",
    )
    args = parser.parse_args()

    if args.stats:
        print(format_bounty_payouts())
        return

    if args.net_usd is None or not args.platform:
        raise SystemExit("--net-usd and --platform are required unless using --stats")

    if args.net_usd <= 0:
        raise SystemExit("net-usd must be positive")

    payload = {
        "lane": LANE,
        "platform": args.platform,
        "report_id": args.report_id,
        "program": args.program,
        "payout_rail": args.payout_rail,
        "net_usd": args.net_usd,
        "notes": args.notes,
    }
    if args.dry_run:
        print(json.dumps({"action": ACTION, "payload": payload, "pnl_usd": args.net_usd}, indent=2))
        return

    log_bounty_payout(
        net_usd=args.net_usd,
        platform=args.platform,
        report_id=args.report_id,
        program=args.program,
        payout_rail=args.payout_rail,
        notes=args.notes,
    )
    earned = year_pnl()
    print(
        f"Logged bounty payout ${args.net_usd:.2f} "
        f"({args.platform}, report: {args.report_id or 'n/a'})"
    )
    print(f"Year PnL: ${earned:.2f}")


if __name__ == "__main__":
    main()
