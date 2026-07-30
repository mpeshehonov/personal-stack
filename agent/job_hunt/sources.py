"""Self-learning job sources: weights, enable/disable, feedback."""

from __future__ import annotations

import json
import logging
from typing import Any

from job_hunt.config import (
    JOBHUNT_HABR_ENABLED,
    JOBHUNT_HH_ENABLED,
    JOBHUNT_HIREHI_ENABLED,
    JOBHUNT_HIRIFY_ENABLED,
    JOBHUNT_TG_ENABLED,
    tg_channel_names,
)
from orchestrator.state import (
    add_job_feedback,
    get_job_lead,
    get_job_source,
    list_job_sources,
    record_source_stats,
    set_job_source,
    update_job_lead_status,
    update_source_weight,
)

logger = logging.getLogger(__name__)

DEFAULT_BOARD_SOURCES = (
    ("hh", "board"),
    ("habr", "board"),
    ("hirify", "board"),
    ("hirehi", "board"),
)

WEIGHT_FLOOR_DISABLE = 0.35
WEIGHT_MIN = 0.1
WEIGHT_MAX = 3.0
DELTA = {
    "like": 0.15,
    "dislike": -0.25,
    "applied": 0.3,
    "interview": 0.5,
}


def source_key_for_vacancy(vacancy: dict[str, Any]) -> str:
    src = (vacancy.get("_source") or "hh").strip()
    if src == "telegram" or src.startswith("tg:"):
        channel = (vacancy.get("_source_channel") or "").strip()
        if not channel:
            vid = str(vacancy.get("id") or "")
            if "/" in vid:
                channel = vid.split("/", 1)[0]
        if src.startswith("tg:") and not channel:
            return src
        return f"tg:{channel}" if channel else "telegram"
    return src


def source_key_for_lead(row: Any) -> str:
    src = (row["source"] or "").strip()
    if src.startswith("tg:"):
        return src
    if src == "telegram":
        eid = (row["external_id"] or "").strip()
        if "/" in eid:
            return f"tg:{eid.split('/', 1)[0]}"
        return "telegram"
    return src or "unknown"


def ensure_default_sources() -> None:
    """Seed board + configured TG channels into job_sources."""
    for key, kind in DEFAULT_BOARD_SOURCES:
        existing = get_job_source(key)
        if existing is None:
            enabled = {
                "hh": JOBHUNT_HH_ENABLED,
                "habr": JOBHUNT_HABR_ENABLED,
                "hirify": JOBHUNT_HIRIFY_ENABLED,
                "hirehi": JOBHUNT_HIREHI_ENABLED,
            }.get(key, True)
            set_job_source(
                key,
                kind=kind,
                weight=1.0,
                enabled=enabled,
                status="active",
            )

    if JOBHUNT_TG_ENABLED:
        for channel in tg_channel_names():
            key = f"tg:{channel}"
            if get_job_source(key) is None:
                set_job_source(
                    key,
                    kind="telegram",
                    weight=1.0,
                    enabled=True,
                    status="active",
                )


def is_source_enabled(source_key: str) -> bool:
    row = get_job_source(source_key)
    if row is None:
        # Unknown TG channel: allow but treat as seed candidate later
        if source_key.startswith("tg:"):
            return JOBHUNT_TG_ENABLED
        board = source_key.split(":", 1)[0]
        return {
            "hh": JOBHUNT_HH_ENABLED,
            "habr": JOBHUNT_HABR_ENABLED,
            "hirify": JOBHUNT_HIRIFY_ENABLED,
            "hirehi": JOBHUNT_HIREHI_ENABLED,
            "telegram": JOBHUNT_TG_ENABLED,
        }.get(board, True)
    if row["status"] == "rejected":
        return False
    if row["status"] == "seed":
        return False
    return bool(row["enabled"]) and float(row["weight"]) >= WEIGHT_FLOOR_DISABLE * 0.5


def enabled_tg_channels() -> list[str]:
    ensure_default_sources()
    channels: list[str] = []
    for row in list_job_sources(kind="telegram"):
        if not row["enabled"] or row["status"] in ("seed", "rejected"):
            continue
        if float(row["weight"]) < WEIGHT_FLOOR_DISABLE:
            continue
        key = row["source_key"]
        if key.startswith("tg:"):
            channels.append(key[3:])
    if channels:
        return channels
    return tg_channel_names() if JOBHUNT_TG_ENABLED else []


def board_enabled(board: str) -> bool:
    ensure_default_sources()
    return is_source_enabled(board)


def mark_fetch_success(source_key: str, fetched: int) -> None:
    record_source_stats(source_key, fetched=fetched, success=True)


def apply_feedback(
    lead_id: int,
    action: str,
    *,
    note: str = "",
) -> dict[str, Any]:
    """Record feedback via Opportunity OS; keep legacy return shape for Telegram."""
    from opportunity.feedback import apply_opportunity_feedback, infer_paywall_reason_from_note
    from opportunity.services import upsert_from_job_lead
    from opportunity.scoring import lead_row_to_vacancy_shape

    action = action.lower().strip()
    if action not in DELTA and action != "reject_reason":
        raise ValueError(f"unknown action: {action}")

    lead = get_job_lead(lead_id)
    if lead is None:
        raise KeyError(f"lead {lead_id} not found")

    # Ensure opportunity row exists (lazy backfill for one lead)
    from opportunity.repository import get_opportunity_by_lead

    if get_opportunity_by_lead(lead_id) is None:
        vacancy = lead_row_to_vacancy_shape(lead)
        try:
            reasons = json.loads(lead["match_reasons_json"] or "[]")
        except json.JSONDecodeError:
            reasons = []
        upsert_from_job_lead(
            lead_id=lead_id,
            vacancy=vacancy,
            match_score=int(lead["match_score"] or 0),
            match_reasons=reasons,
            lead_status=lead["status"] or "new",
        )

    reason = infer_paywall_reason_from_note(note)
    source_key = source_key_for_lead(lead)
    # Hirify «Мимо» without explicit fit reason → treat as paywall/actionability
    if (
        action == "dislike"
        and source_key == "hirify"
        and not reason
    ):
        reason = "paywall"
    if action == "dislike" and note.lower() in ("bad_fit", "mismatch", "не релевант"):
        reason = note  # punish source

    if action == "reject_reason":
        add_job_feedback(lead_id, action=action, note=note, source_key=source_key)
        return {
            "lead_id": lead_id,
            "action": action,
            "source_key": source_key,
            "weight_before": 0,
            "weight_after": 0,
            "disabled": False,
            "title": lead["title"],
            "company": lead["company"],
        }

    result = apply_opportunity_feedback(
        lead_id=lead_id,
        action=action,
        reason=reason,
    )
    src = result.get("source") or {}
    return {
        "lead_id": lead_id,
        "action": action,
        "source_key": src.get("source_key") or source_key,
        "weight_before": src.get("weight_before", 0),
        "weight_after": src.get("weight_after", 0),
        "disabled": bool(src.get("disabled")),
        "source_weight_skipped": bool(src.get("source_weight_skipped")),
        "title": result.get("title") or lead["title"],
        "company": result.get("company") or lead["company"],
        "opportunity_id": result.get("opportunity_id"),
        "next_action": result.get("next_action"),
    }


def propose_source(source_key: str, *, notes: str = "") -> None:
    """Add a seed source waiting for /approve source."""
    kind = "telegram" if source_key.startswith("tg:") else "board"
    set_job_source(
        source_key,
        kind=kind,
        weight=1.0,
        enabled=False,
        status="seed",
        notes=notes,
    )


def approve_source(source_key: str) -> bool:
    row = get_job_source(source_key)
    if row is None:
        return False
    set_job_source(
        source_key,
        kind=row["kind"],
        weight=max(float(row["weight"]), 1.0),
        enabled=True,
        status="active",
        notes=row["notes"] or "",
    )
    return True


def reject_source(source_key: str) -> bool:
    row = get_job_source(source_key)
    if row is None:
        return False
    set_job_source(
        source_key,
        kind=row["kind"],
        weight=float(row["weight"]),
        enabled=False,
        status="rejected",
        notes=row["notes"] or "",
    )
    return True


def format_sources_plain() -> str:
    ensure_default_sources()
    rows = list_job_sources()
    if not rows:
        return "Источники ещё не инициализированы."

    lines = ["Источники (вес / статус):", ""]
    for row in rows:
        flag = "on" if row["enabled"] and row["status"] == "active" else row["status"]
        if not row["enabled"] and row["status"] == "active":
            flag = "off"
        lines.append(
            f"- {row['source_key']}: вес {float(row['weight']):.2f}, {flag}"
        )
    lines.extend(
        [
            "",
            "Команды: /jobs like <id>, /jobs dislike <id>, /approve source <key>, /reject source <key>",
        ]
    )
    return "\n".join(lines)


def sources_report_snippet() -> str:
    ensure_default_sources()
    rows = [r for r in list_job_sources() if r["status"] == "active"]
    if not rows:
        return "—"
    ranked = sorted(rows, key=lambda r: float(r["weight"]), reverse=True)
    top = ranked[:3]
    bottom = list(reversed(ranked[-3:])) if len(ranked) > 3 else []
    lines = []
    if top:
        lines.append(
            "Лучшие: "
            + ", ".join(f"{r['source_key']} ({float(r['weight']):.2f})" for r in top)
        )
    disabled = [r for r in list_job_sources() if not r["enabled"] or r["status"] != "active"]
    if disabled:
        lines.append(
            "Выкл/seed: " + ", ".join(r["source_key"] for r in disabled[:5])
        )
    elif bottom:
        lines.append(
            "Слабые: "
            + ", ".join(f"{r['source_key']} ({float(r['weight']):.2f})" for r in bottom)
        )
    return "\n".join(lines) if lines else "—"
