"""Sync fulfilled A4 checkout orders from site data into finance_log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from finance.a4_sales import log_a4_sale
from orchestrator.config import STACK_DIR

DEFAULT_ORDERS_PATH = STACK_DIR / "data" / "checkout" / "orders.json"


def load_orders(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    orders = data.get("orders", [])
    return orders if isinstance(orders, list) else []


def sync_checkout_orders(
    path: Path | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    orders_path = path or DEFAULT_ORDERS_PATH
    orders = load_orders(orders_path)
    synced: list[str] = []
    skipped: list[str] = []

    for order in orders:
        if order.get("status") != "fulfilled":
            continue
        if order.get("synced_finance"):
            skipped.append(str(order.get("order_id", "")))
            continue
        order_id = str(order.get("order_id") or order.get("payment_id") or "")
        net_usd = float(order.get("net_usd") or 0)
        if net_usd <= 0 or not order_id:
            skipped.append(order_id or "invalid")
            continue
        provider = str(order.get("provider", "crypto"))
        if dry_run:
            synced.append(order_id)
            continue
        log_a4_sale(
            net_usd=net_usd,
            order_id=order_id,
            notes=f"checkout_sync:{provider}",
        )
        order["synced_finance"] = True
        synced.append(order_id)

    if not dry_run and synced:
        orders_path.parent.mkdir(parents=True, exist_ok=True)
        orders_path.write_text(
            json.dumps({"orders": orders}, indent=2),
            encoding="utf-8",
        )

    return {
        "path": str(orders_path),
        "synced": synced,
        "skipped": skipped,
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync A4 crypto checkout orders to finance_log")
    parser.add_argument("--orders-path", type=Path, default=DEFAULT_ORDERS_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = sync_checkout_orders(args.orders_path, dry_run=args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
