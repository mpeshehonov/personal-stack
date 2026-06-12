"""Paper-trade signal filters for multi-venue scans.

Rules are documented in agent/memory/lessons/azuro_paper_rules.md.
Env overrides via .env.finance (see secrets/.env.finance.template).
"""

from __future__ import annotations

import os
from typing import Any

from orchestrator.config import load_env_file

DEFAULT_MIN_EDGE_PCT = 3.0
DEFAULT_MAX_ODDS_DRIFT_PCT = 5.0
DEFAULT_MIN_TURNOVER_USD = 100.0
DEFAULT_LEAGUE_WHITELIST = (
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "UEFA Champions League",
    "UEFA Europa League",
    "NBA",
    "NHL",
    "NFL",
    "MLB",
)


def _cfg_float(key: str, default: float) -> float:
    load_env_file(".env.finance")
    raw = os.environ.get(key, "")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _league_whitelist() -> set[str]:
    load_env_file(".env.finance")
    raw = os.environ.get("AZURO_LEAGUE_WHITELIST", "")
    if raw.strip():
        return {s.strip() for s in raw.split(",") if s.strip()}
    return set(DEFAULT_LEAGUE_WHITELIST)


def passes_liquidity_floor(
    market: dict[str, Any],
    *,
    min_turnover: float | None = None,
) -> tuple[bool, str | None]:
    """Azuro: skip markets below turnover floor. Other venues pass."""
    if market.get("venue") != "azuro":
        return True, None
    floor = min_turnover if min_turnover is not None else _cfg_float(
        "AZURO_MIN_TURNOVER_USD", DEFAULT_MIN_TURNOVER_USD
    )
    turnover = market.get("turnover")
    if turnover is None:
        return False, "missing turnover"
    try:
        value = float(turnover)
    except (TypeError, ValueError):
        return False, "invalid turnover"
    if value < floor:
        return False, f"turnover ${value:.0f} < floor ${floor:.0f}"
    return True, None


def passes_odds_drift(
    market: dict[str, Any],
    *,
    max_drift_pct: float | None = None,
) -> tuple[bool, str | None]:
    """Skip when odds moved beyond threshold (requires odds_drift_pct on market)."""
    drift = market.get("odds_drift_pct")
    if drift is None:
        return True, None
    limit = max_drift_pct if max_drift_pct is not None else _cfg_float(
        "AZURO_MAX_ODDS_DRIFT_PCT", DEFAULT_MAX_ODDS_DRIFT_PCT
    )
    try:
        value = abs(float(drift))
    except (TypeError, ValueError):
        return False, "invalid odds_drift_pct"
    if value > limit:
        return False, f"odds drift {value:.1f}% > max {limit:.1f}%"
    return True, None


def passes_league_whitelist(
    market: dict[str, Any],
    *,
    leagues: set[str] | None = None,
) -> tuple[bool, str | None]:
    """Azuro: only whitelisted leagues. Empty whitelist env disables filter."""
    if market.get("venue") != "azuro":
        return True, None
    allowed = leagues if leagues is not None else _league_whitelist()
    if not allowed:
        return True, None
    league = str(market.get("league") or "").strip()
    if not league:
        return False, "missing league"
    if league not in allowed:
        return False, f"league not whitelisted: {league}"
    return True, None


def passes_min_edge(
    market: dict[str, Any],
    *,
    min_edge_pct: float | None = None,
) -> tuple[bool, str | None]:
    """Skip when modeled edge below floor (requires edge_pct on market)."""
    edge = market.get("edge_pct")
    if edge is None:
        return True, None
    floor = min_edge_pct if min_edge_pct is not None else _cfg_float(
        "AZURO_MIN_EDGE_PCT", DEFAULT_MIN_EDGE_PCT
    )
    try:
        value = float(edge)
    except (Type, ValueError):
        return False, "invalid edge_pct"
    if value < floor:
        return False, f"edge {value:.1f}% < min {floor:.1f}%"
    return True, None


def filter_scan_markets(
    markets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply paper-trade filters; return (passed, rejected with reasons)."""
    passed: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    checks = (
        passes_liquidity_floor,
        passes_league_whitelist,
        passes_odds_drift,
        passes_min_edge,
    )

    for market in markets:
        reasons: list[str] = []
        for check in checks:
            ok, reason = check(market)
            if not ok and reason:
                reasons.append(reason)
        if reasons:
            rejected.append({**market, "reject_reasons": reasons})
        else:
            passed.append(market)

    return passed, rejected
