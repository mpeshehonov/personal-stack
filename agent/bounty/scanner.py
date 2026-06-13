"""Bug bounty semi-auto pipeline: agent research → draft → approve → submit."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from bounty.config import (
    BOUNTY_ENABLED,
    BOUNTY_MAX_PENDING,
    BOUNTY_RESEARCH_COOLDOWN_HOURS,
    KV_LAST_RESEARCH,
    KV_PROGRAM_INDEX,
)
from bounty.models import BountyScanResult
from bounty.programs import WEB_JS_PROGRAMS, program_by_index
from bounty.researcher import finding_to_draft, research_program
from orchestrator.state import (
    add_bounty_draft,
    count_bounty_drafts_by_status,
    kv_get,
    kv_set,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _next_program_index() -> int:
    raw = kv_get(KV_PROGRAM_INDEX, "0")
    try:
        current = int(raw)
    except ValueError:
        current = 0
    nxt = (current + 1) % len(WEB_JS_PROGRAMS)
    kv_set(KV_PROGRAM_INDEX, str(nxt))
    return current


def _research_allowed() -> bool:
    last = _parse_ts(kv_get(KV_LAST_RESEARCH))
    if not last:
        return True
    return _utcnow() - last >= timedelta(hours=BOUNTY_RESEARCH_COOLDOWN_HOURS)


def daily_bounty_scan(*, force: bool = False) -> BountyScanResult:
    """Run one agent research cycle; create draft only for submit-ready findings."""
    result = BountyScanResult()

    if not BOUNTY_ENABLED:
        result.skipped_reason = "disabled"
        result.message = "Bounty отключён (BOUNTY_ENABLED=false)"
        return result

    pending = count_bounty_drafts_by_status("pending")
    if pending >= BOUNTY_MAX_PENDING:
        result.skipped_reason = "pending_limit"
        result.message = f"Уже {pending} pending-отчётов — жду /approve или /reject"
        return result

    if not force and not _research_allowed():
        result.skipped_reason = "cooldown"
        result.message = (
            f"Cooldown {BOUNTY_RESEARCH_COOLDOWN_HOURS}ч — следующий ресёрч позже"
        )
        return result

    program = program_by_index(_next_program_index())
    result.researched_program = program.name

    try:
        finding = research_program(program)
    except Exception as e:
        logger.exception("Bounty research failed for %s", program.name)
        kv_set(KV_LAST_RESEARCH, _utcnow().isoformat())
        result.message = f"Ошибка ресёрча {program.name}: {e}"
        return result

    kv_set(KV_LAST_RESEARCH, _utcnow().isoformat())

    if not finding:
        result.finding_found = False
        result.message = (
            f"Программа **{program.name}**: submit-ready finding не найден. "
            "Черновик не создан."
        )
        return result

    title, body, meta = finding_to_draft(finding)
    draft_id = add_bounty_draft(title, body, meta)
    result.draft_ids = [draft_id]
    result.finding_found = True
    result.message = (
        f"Готовый отчёт #{draft_id} — **{finding.title}** "
        f"({finding.severity}, {program.name}). "
        "Проверь `/bounty`, затем `/approve bounty {id}` для авто-сабмита."
    ).replace("{id}", str(draft_id))
    return result


def manual_bounty_research() -> BountyScanResult:
    """Force research ignoring cooldown (still respects pending limit)."""
    return daily_bounty_scan(force=True)
