"""Bug bounty semi-auto pipeline: purge → multi-program deep research → draft."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from bounty.config import (
    BOUNTY_ENABLED,
    BOUNTY_MAX_PENDING,
    BOUNTY_PROGRAMS_PER_CYCLE,
    BOUNTY_RESEARCH_COOLDOWN_HOURS,
    KV_LAST_RESEARCH,
    KV_PROGRAM_INDEX,
)
from bounty.models import BountyScanResult
from bounty.programs import WEB_JS_PROGRAMS, program_by_index
from bounty.purge import purge_non_submit_drafts
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
    """Purge weak drafts, run deep research on up to N programs."""
    result = BountyScanResult()

    if not BOUNTY_ENABLED:
        result.skipped_reason = "disabled"
        result.message = "Bounty отключён (BOUNTY_ENABLED=false)"
        return result

    result.purged_ids = purge_non_submit_drafts(revalidate=True)
    if result.purged_ids:
        result.research_log.append(
            f"Отсеяно pending: {', '.join(f'#{i}' for i in result.purged_ids)}"
        )

    pending = count_bounty_drafts_by_status("pending")
    if pending >= BOUNTY_MAX_PENDING:
        result.skipped_reason = "pending_limit"
        result.message = (
            f"Уже {pending} submit-ready отчётов — жду /approve или /reject"
        )
        return result

    if not force and not _research_allowed():
        result.skipped_reason = "cooldown"
        result.message = (
            f"Cooldown {BOUNTY_RESEARCH_COOLDOWN_HOURS}ч — следующий deep research позже"
        )
        return result

    attempts = max(1, BOUNTY_PROGRAMS_PER_CYCLE)
    for _ in range(attempts):
        if count_bounty_drafts_by_status("pending") >= BOUNTY_MAX_PENDING:
            break

        idx = _next_program_index()
        program = program_by_index(idx)
        result.programs_tried.append(program.name)
        result.researched_program = program.name

        try:
            finding, log_line = research_program(program)
        except Exception as e:
            logger.exception("Bounty research failed for %s", program.name)
            result.research_log.append(f"{program.name}: ошибка — {e}")
            continue

        result.research_log.append(log_line)

        if finding:
            title, body, meta = finding_to_draft(finding)
            draft_id = add_bounty_draft(title, body, meta)
            result.draft_ids.append(draft_id)
            result.finding_found = True
            score = finding.quality_score or "—"
            result.message = (
                f"Submit-ready **#{draft_id}** — {finding.title} "
                f"({finding.severity}, {program.name}, QA score {score}). "
                f"`/approve bounty {draft_id}`"
            )
            kv_set(KV_LAST_RESEARCH, _utcnow().isoformat())
            return result

    kv_set(KV_LAST_RESEARCH, _utcnow().isoformat())
    tried = ", ".join(result.programs_tried) or "—"
    log = "\n".join(f"- {line}" for line in result.research_log[-6:])
    result.message = (
        f"Deep research ({attempts} программ): **{tried}**\n"
        f"Submit-ready finding не найден.\n\n{log}"
    )
    return result


def manual_bounty_research() -> BountyScanResult:
    """Force deep research ignoring cooldown."""
    return daily_bounty_scan(force=True)


def purge_bounty_queue() -> BountyScanResult:
    """Manual purge of non-submit pending drafts."""
    result = BountyScanResult()
    result.purged_ids = purge_non_submit_drafts(revalidate=True)
    if result.purged_ids:
        result.message = f"Отклонено: {', '.join(f'#{i}' for i in result.purged_ids)}"
    else:
        result.message = "Нечего отсеивать — все pending проходят validation."
    return result
