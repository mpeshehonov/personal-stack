"""Annual earning goal tracking."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from orchestrator.config import load_env_file
from orchestrator.format_ru import format_date_ru, format_usd
from orchestrator.state import year_pnl


def goal_config() -> dict:
    load_env_file(".env.finance")
    return {
        "target_usd": float(os.environ.get("ANNUAL_GOAL_USD", "15000")),
        "deadline": os.environ.get("ANNUAL_GOAL_DEADLINE", "2026-12-31"),
        "year": int(os.environ.get("ANNUAL_GOAL_YEAR", "2026")),
    }


def goal_progress() -> dict:
    cfg = goal_config()
    earned = year_pnl(cfg["year"])
    target = cfg["target_usd"]
    remaining = max(0.0, target - earned)
    pct = (earned / target * 100) if target > 0 else 0.0
    deadline = datetime.strptime(cfg["deadline"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_left = max(0, (deadline - datetime.now(timezone.utc)).days)
    daily_needed = remaining / days_left if days_left > 0 else remaining
    return {
        "target_usd": target,
        "earned_usd": round(earned, 2),
        "remaining_usd": round(remaining, 2),
        "progress_pct": round(pct, 1),
        "deadline": cfg["deadline"],
        "days_left": days_left,
        "daily_needed_usd": round(daily_needed, 2),
    }


def format_goal_progress() -> str:
    p = goal_progress()
    pct = (
        f"{int(p['progress_pct'])}%"
        if p["progress_pct"] == round(p["progress_pct"])
        else f"{p['progress_pct']:.1f}%"
    )
    return (
        f"Goal {format_usd(p['target_usd'])} by {format_date_ru(p['deadline'])}: "
        f"{format_usd(p['earned_usd'])} earned ({pct}), "
        f"{format_usd(p['remaining_usd'])} left, "
        f"~{format_usd(p['daily_needed_usd'])}/day for {p['days_left']} days"
    )
