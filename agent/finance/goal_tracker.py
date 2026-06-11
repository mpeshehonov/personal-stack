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
        "milestone_usd": float(os.environ.get("MILESTONE_GOAL_USD", "1000")),
        "milestone_deadline": os.environ.get("MILESTONE_GOAL_DEADLINE", "2026-09-30"),
        "milestone_label": os.environ.get("MILESTONE_GOAL_LABEL", "autonomous $1k"),
    }


def _progress_slice(earned: float, target: float, deadline_str: str) -> dict:
    remaining = max(0.0, target - earned)
    pct = (earned / target * 100) if target > 0 else 0.0
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_left = max(0, (deadline - datetime.now(timezone.utc)).days)
    daily_needed = remaining / days_left if days_left > 0 else remaining
    return {
        "target_usd": target,
        "earned_usd": round(earned, 2),
        "remaining_usd": round(remaining, 2),
        "progress_pct": round(pct, 1),
        "deadline": deadline_str,
        "days_left": days_left,
        "daily_needed_usd": round(daily_needed, 2),
    }


def goal_progress() -> dict:
    cfg = goal_config()
    earned = year_pnl(cfg["year"])
    return _progress_slice(earned, cfg["target_usd"], cfg["deadline"])


def milestone_progress() -> dict:
    cfg = goal_config()
    earned = year_pnl(cfg["year"])
    base = _progress_slice(earned, cfg["milestone_usd"], cfg["milestone_deadline"])
    base["label"] = cfg["milestone_label"]
    return base


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


def format_milestone_progress() -> str:
    m = milestone_progress()
    pct = (
        f"{int(m['progress_pct'])}%"
        if m["progress_pct"] == round(m["progress_pct"])
        else f"{m['progress_pct']:.1f}%"
    )
    return (
        f"M1 {m['label']}: {format_usd(m['earned_usd'])} / {format_usd(m['target_usd'])} "
        f"({pct}) by {format_date_ru(m['deadline'])}"
    )
