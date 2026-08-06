"""Re-check stored JOB/CLIENT links — archive closed FL/Kwork/HH."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

from opportunity.client_scan import (
    is_dead_url,
    validate_fl_project,
    validate_kwork_project,
)
from orchestrator.state import get_conn

logger = logging.getLogger(__name__)

_HH_ID_RE = re.compile(r"hh\.ru/vacancy/(\d+)", re.I)
RATE_LIMIT_SEC = 0.4


def _archive_opportunity(conn, opp_id: int, *, reason: str) -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    row = conn.execute(
        "SELECT analysis_json FROM opportunities WHERE id=?", (opp_id,)
    ).fetchone()
    analysis: dict[str, Any] = {}
    if row:
        try:
            analysis = json.loads(row["analysis_json"] or "{}")
        except json.JSONDecodeError:
            analysis = {}
    analysis["closed_reason"] = reason
    analysis["closed_at"] = now
    conn.execute(
        """
        UPDATE opportunities
        SET status='archived', next_action='ARCHIVE', next_action_priority='LOW',
            analysis_json=?, updated_at=?
        WHERE id=?
        """,
        (json.dumps(analysis, ensure_ascii=False), now, opp_id),
    )


def _reject_job_lead(conn, lead_id: int, *, note: str = "") -> None:
    conn.execute(
        "UPDATE job_leads SET status='rejected' WHERE id=? AND status IN ('new','liked')",
        (lead_id,),
    )


def validate_hh_vacancy_url(url: str) -> dict[str, Any]:
    m = _HH_ID_RE.search(url or "")
    if not m:
        return {"ok": True, "reason": "not_hh"}  # not our concern
    vid = m.group(1)
    try:
        from job_hunt.hh_client import fetch_hh_vacancy_api

        data = fetch_hh_vacancy_api(vid)
        if data is None:
            # API often 403 from NL — don't archive on fetch failure
            return {"ok": True, "reason": "hh_fetch_blocked"}
    except Exception as exc:
        return {"ok": True, "reason": f"hh_fetch_error:{exc}"}
    if data.get("archived") is True:
        return {"ok": False, "reason": "hh_archived"}
    return {"ok": True, "reason": "open", "title": data.get("name")}


def validate_open_url(url: str) -> dict[str, Any]:
    """Return {ok, reason} — ok=False means archive."""
    url = (url or "").strip()
    if not url:
        return {"ok": False, "reason": "empty_url"}
    if is_dead_url(url):
        return {"ok": False, "reason": "dead_habr"}
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if "fl.ru" in host and "/projects/" in path:
        return validate_fl_project(url)
    if "kwork.ru" in host and "/projects/" in path:
        return validate_kwork_project(url)
    if "hh.ru" in host and "/vacancy/" in path:
        return validate_hh_vacancy_url(url)
    # TG posts / generic career pages — can't prove closed cheaply
    return {"ok": True, "reason": "unchecked"}


def revalidate_client_opportunities(*, limit: int = 40) -> dict[str, Any]:
    """Archive CLIENT rows whose FL/Kwork (etc.) links are closed."""
    checked = 0
    archived = 0
    reasons: dict[str, int] = {}
    try:
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, source, source_url, title FROM opportunities
                WHERE type = 'CLIENT'
                  AND status IN ('new', 'saved', 'reviewing')
                ORDER BY overall_score DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            for row in rows:
                url = row["source_url"] or ""
                src = (row["source"] or "").lower()
                title = (row["title"] or "").lower()
                checked += 1
                if (
                    src.startswith("client:habr:")
                    or "habr freelance" in title
                    or "хабр фриланс" in title
                ):
                    _archive_opportunity(conn, int(row["id"]), reason="habr_dead")
                    archived += 1
                    reasons["habr_dead"] = reasons.get("habr_dead", 0) + 1
                    continue
                result = validate_open_url(url)
                if not result.get("ok"):
                    why = str(result.get("reason") or "closed")
                    _archive_opportunity(conn, int(row["id"]), reason=why)
                    archived += 1
                    reasons[why] = reasons.get(why, 0) + 1
                if "fl.ru" in url or "kwork.ru" in url or "hh.ru" in url:
                    time.sleep(RATE_LIMIT_SEC)
    except Exception as exc:
        logger.warning("revalidate_client_opportunities failed: %s", exc)
        return {"checked": checked, "archived": archived, "reasons": reasons, "error": str(exc)}

    logger.info(
        "CLIENT revalidate: checked=%s archived=%s reasons=%s",
        checked,
        archived,
        reasons,
    )
    return {"checked": checked, "archived": archived, "reasons": reasons}


def revalidate_job_leads(*, limit: int = 40) -> dict[str, Any]:
    """Archive/reject JOB leads whose HH/FL/Kwork links are closed."""
    checked = 0
    archived = 0
    reasons: dict[str, int] = {}
    try:
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT o.id AS opp_id, o.source_url, o.job_lead_id, jl.url AS lead_url, jl.status AS lead_status
                FROM opportunities o
                LEFT JOIN job_leads jl ON jl.id = o.job_lead_id
                WHERE o.type = 'JOB'
                  AND o.status IN ('new', 'saved', 'reviewing')
                ORDER BY o.overall_score DESC, o.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            for row in rows:
                url = (row["source_url"] or row["lead_url"] or "").strip()
                if not url:
                    continue
                # Only revalidate URLs we can prove
                host = urlparse(url).netloc.lower()
                if not any(x in host for x in ("hh.ru", "fl.ru", "kwork.ru")) and not is_dead_url(
                    url
                ):
                    continue
                checked += 1
                result = validate_open_url(url)
                if not result.get("ok"):
                    why = str(result.get("reason") or "closed")
                    _archive_opportunity(conn, int(row["opp_id"]), reason=why)
                    if row["job_lead_id"]:
                        _reject_job_lead(conn, int(row["job_lead_id"]), note=why)
                    archived += 1
                    reasons[why] = reasons.get(why, 0) + 1
                time.sleep(RATE_LIMIT_SEC)
    except Exception as exc:
        logger.warning("revalidate_job_leads failed: %s", exc)
        return {"checked": checked, "archived": archived, "reasons": reasons, "error": str(exc)}

    logger.info(
        "JOB revalidate: checked=%s archived=%s reasons=%s", checked, archived, reasons
    )
    return {"checked": checked, "archived": archived, "reasons": reasons}


def refresh_open_pipeline(*, clients_limit: int = 40, jobs_limit: int = 40) -> dict[str, Any]:
    """Full actualization: close dead links + light research backfill for jobs."""
    clients = revalidate_client_opportunities(limit=clients_limit)
    jobs = revalidate_job_leads(limit=jobs_limit)
    research_n = 0
    try:
        from opportunity.services import refresh_research_for_opportunities

        research_n = refresh_research_for_opportunities(limit=8)
    except Exception as exc:
        logger.warning("research refresh skipped: %s", exc)
    return {
        "clients": clients,
        "jobs": jobs,
        "research_updated": research_n,
        "archived_total": int(clients.get("archived") or 0)
        + int(jobs.get("archived") or 0),
    }
