"""Read-only CEX grid parameter calculator — levels only, no live orders."""

from __future__ import annotations

import math
from typing import Any, Literal

GridMode = Literal["arithmetic", "geometric"]


def compute_grid_levels(
    *,
    lower_price: float,
    upper_price: float,
    grid_count: int,
    total_capital_usd: float,
    mode: GridMode = "arithmetic",
) -> dict[str, Any]:
    """
    Compute grid buy levels and per-level USD allocation.

    Returns sorted levels from lower to upper with cumulative capital split evenly.
    """
    if lower_price <= 0 or upper_price <= 0:
        raise ValueError("prices must be positive")
    if lower_price >= upper_price:
        raise ValueError("lower_price must be below upper_price")
    if grid_count < 2:
        raise ValueError("grid_count must be at least 2")
    if total_capital_usd <= 0:
        raise ValueError("total_capital_usd must be positive")

    if mode == "arithmetic":
        step = (upper_price - lower_price) / (grid_count - 1)
        prices = [lower_price + step * i for i in range(grid_count)]
    else:
        ratio = (upper_price / lower_price) ** (1 / (grid_count - 1))
        prices = [lower_price * (ratio**i) for i in range(grid_count)]

    per_level_usd = round(total_capital_usd / grid_count, 2)
    levels: list[dict[str, Any]] = []
    for i, price in enumerate(prices):
        size_usd = per_level_usd
        if i == grid_count - 1:
            size_usd = round(total_capital_usd - per_level_usd * (grid_count - 1), 2)
        levels.append(
            {
                "index": i + 1,
                "price": round(price, 8),
                "size_usd": size_usd,
                "est_qty": round(size_usd / price, 8) if price else 0,
            }
        )

    span_pct = round((upper_price - lower_price) / lower_price * 100, 2)
    return {
        "mode": mode,
        "lower_price": lower_price,
        "upper_price": upper_price,
        "grid_count": grid_count,
        "total_capital_usd": total_capital_usd,
        "span_pct": span_pct,
        "per_level_usd_avg": per_level_usd,
        "levels": levels,
    }


def suggest_grid_from_price(
    last_price: float,
    *,
    span_pct: float = 10.0,
    grid_count: int = 5,
    total_capital_usd: float = 300.0,
    mode: GridMode = "arithmetic",
) -> dict[str, Any]:
    """Symmetric grid around last price (read-only suggestion)."""
    if last_price <= 0:
        raise ValueError("last_price must be positive")
    half = span_pct / 100 / 2
    lower = last_price * (1 - half)
    upper = last_price * (1 + half)
    result = compute_grid_levels(
        lower_price=lower,
        upper_price=upper,
        grid_count=grid_count,
        total_capital_usd=total_capital_usd,
        mode=mode,
    )
    result["anchor_price"] = last_price
    result["span_pct"] = span_pct
    return result


def format_grid_summary(grid: dict[str, Any], symbol: str = "") -> str:
    """Human-readable one-liner for daily logs."""
    prefix = f"{symbol} " if symbol else ""
    lo = grid["lower_price"]
    hi = grid["upper_price"]
    n = grid["grid_count"]
    cap = grid["total_capital_usd"]
    return (
        f"{prefix}grid {n} levels ${lo:,.2f}–${hi:,.2f} "
        f"({grid.get('span_pct', 0):.1f}% span), ${cap:,.0f} capital"
    )


def grid_preview_for_markets(
    markets: list[dict[str, Any]],
    *,
    span_pct: float = 10.0,
    grid_count: int = 5,
    total_capital_usd: float = 300.0,
) -> list[dict[str, Any]]:
    """Build grid suggestions for CEX pseudo-markets from a scan batch."""
    previews: list[dict[str, Any]] = []
    for m in markets:
        if m.get("venue") != "cex":
            continue
        symbol = str(m.get("id") or m.get("condition_id") or "")
        last_raw = m.get("last_price")
        if last_raw is None:
            continue
        try:
            last = float(last_raw)
        except (TypeError, ValueError):
            continue
        if last <= 0 or not math.isfinite(last):
            continue
        grid = suggest_grid_from_price(
            last,
            span_pct=span_pct,
            grid_count=grid_count,
            total_capital_usd=total_capital_usd,
        )
        previews.append({"symbol": symbol, "grid": grid, "summary": format_grid_summary(grid, symbol)})
    return previews
