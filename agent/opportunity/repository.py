"""SQLite repository for opportunities (extends state.sqlite)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from orchestrator.state import get_conn
from opportunity.models import Opportunity, OpportunityStatus, OpportunityType


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_opportunity_schema(conn: sqlite3.Connection | None = None) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        company_or_entity TEXT NOT NULL DEFAULT '',
        source TEXT NOT NULL DEFAULT '',
        source_url TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'new',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        raw_payload TEXT NOT NULL DEFAULT '{}',
        normalized_payload TEXT NOT NULL DEFAULT '{}',
        scores_json TEXT NOT NULL DEFAULT '{}',
        analysis_json TEXT NOT NULL DEFAULT '{}',
        next_action TEXT NOT NULL DEFAULT 'REVIEW',
        next_action_priority TEXT NOT NULL DEFAULT 'MEDIUM',
        overall_score INTEGER NOT NULL DEFAULT 0,
        job_lead_id INTEGER UNIQUE,
        FOREIGN KEY (job_lead_id) REFERENCES job_leads(id)
    );
    CREATE INDEX IF NOT EXISTS idx_opportunities_overall
        ON opportunities(overall_score DESC);
    CREATE INDEX IF NOT EXISTS idx_opportunities_status
        ON opportunities(status);
    CREATE INDEX IF NOT EXISTS idx_opportunities_type
        ON opportunities(type);

    CREATE TABLE IF NOT EXISTS opportunity_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opportunity_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT '',
        ts TEXT NOT NULL,
        meta_json TEXT NOT NULL DEFAULT '{}',
        FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
    );
    CREATE INDEX IF NOT EXISTS idx_opp_feedback_opp
        ON opportunity_feedback(opportunity_id);

    CREATE TABLE IF NOT EXISTS opportunity_metrics_daily (
        day TEXT PRIMARY KEY,
        payload_json TEXT NOT NULL DEFAULT '{}'
    );
    """
    if conn is not None:
        conn.executescript(ddl)
        return
    with get_conn() as c:
        c.executescript(ddl)


def _row_to_opportunity(row: sqlite3.Row) -> Opportunity:
    def _loads(key: str) -> Any:
        try:
            return json.loads(row[key] or "{}")
        except json.JSONDecodeError:
            return {}

    return Opportunity(
        id=int(row["id"]),
        type=OpportunityType(row["type"]),
        title=row["title"],
        company_or_entity=row["company_or_entity"] or "",
        source=row["source"] or "",
        source_url=row["source_url"] or "",
        status=OpportunityStatus(row["status"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        raw_payload=_loads("raw_payload"),
        normalized_payload=_loads("normalized_payload"),
        scores=_loads("scores_json"),
        analysis=_loads("analysis_json"),
        next_action=row["next_action"],
        next_action_priority=row["next_action_priority"],
        job_lead_id=row["job_lead_id"],
        overall_score=int(row["overall_score"] or 0),
    )


def upsert_job_opportunity(
    *,
    job_lead_id: int,
    title: str,
    company: str,
    source: str,
    source_url: str,
    status: str,
    raw_payload: dict[str, Any],
    normalized_payload: dict[str, Any],
    scores: dict[str, Any],
    analysis: dict[str, Any],
    next_action: str,
    next_action_priority: str,
    overall_score: int,
) -> int:
    ensure_opportunity_schema()
    now = _utcnow()
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM opportunities WHERE job_lead_id = ?",
            (job_lead_id,),
        ).fetchone()
        raw_s = json.dumps(raw_payload, ensure_ascii=False)
        norm_s = json.dumps(normalized_payload, ensure_ascii=False)
        scores_s = json.dumps(scores, ensure_ascii=False)
        analysis_s = json.dumps(analysis, ensure_ascii=False)
        if existing:
            conn.execute(
                """
                UPDATE opportunities SET
                    title=?, company_or_entity=?, source=?, source_url=?,
                    status=?, updated_at=?, raw_payload=?, normalized_payload=?,
                    scores_json=?, analysis_json=?, next_action=?,
                    next_action_priority=?, overall_score=?
                WHERE job_lead_id=?
                """,
                (
                    title,
                    company,
                    source,
                    source_url,
                    status,
                    now,
                    raw_s,
                    norm_s,
                    scores_s,
                    analysis_s,
                    next_action,
                    next_action_priority,
                    int(overall_score),
                    job_lead_id,
                ),
            )
            return int(existing["id"])

        cur = conn.execute(
            """
            INSERT INTO opportunities(
                type, title, company_or_entity, source, source_url, status,
                created_at, updated_at, raw_payload, normalized_payload,
                scores_json, analysis_json, next_action, next_action_priority,
                overall_score, job_lead_id
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                OpportunityType.JOB.value,
                title,
                company,
                source,
                source_url,
                status,
                now,
                now,
                raw_s,
                norm_s,
                scores_s,
                analysis_s,
                next_action,
                next_action_priority,
                int(overall_score),
                job_lead_id,
            ),
        )
        return int(cur.lastrowid)


def get_opportunity(opp_id: int) -> Opportunity | None:
    ensure_opportunity_schema()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM opportunities WHERE id = ?", (opp_id,)
        ).fetchone()
        return _row_to_opportunity(row) if row else None


def get_opportunity_by_lead(job_lead_id: int) -> Opportunity | None:
    ensure_opportunity_schema()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM opportunities WHERE job_lead_id = ?",
            (job_lead_id,),
        ).fetchone()
        return _row_to_opportunity(row) if row else None


def list_opportunities(
    *,
    status: str | None = None,
    opp_type: str | None = OpportunityType.JOB.value,
    limit: int = 20,
    min_overall: int = 0,
) -> list[Opportunity]:
    ensure_opportunity_schema()
    clauses = ["overall_score >= ?"]
    params: list[Any] = [min_overall]
    if status:
        clauses.append("status = ?")
        params.append(status)
    if opp_type:
        clauses.append("type = ?")
        params.append(opp_type)
    params.append(limit)
    sql = f"""
        SELECT * FROM opportunities
        WHERE {' AND '.join(clauses)}
        ORDER BY overall_score DESC, id DESC
        LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_opportunity(r) for r in rows]


def update_opportunity_analysis(
    opp_id: int,
    analysis: dict[str, Any],
    *,
    next_action: str | None = None,
    next_action_priority: str | None = None,
    company_or_entity: str | None = None,
) -> None:
    """Patch analysis_json (and optional next_action / company) after contact research."""
    ensure_opportunity_schema()
    now = _utcnow()
    with get_conn() as conn:
        fields = ["analysis_json=?", "updated_at=?"]
        params: list[Any] = [json.dumps(analysis, ensure_ascii=False), now]
        if next_action is not None:
            fields.append("next_action=?")
            params.append(next_action)
        if next_action_priority is not None:
            fields.append("next_action_priority=?")
            params.append(next_action_priority)
        if company_or_entity is not None:
            fields.append("company_or_entity=?")
            params.append(company_or_entity)
        params.append(opp_id)
        conn.execute(
            f"UPDATE opportunities SET {', '.join(fields)} WHERE id=?",
            params,
        )


def update_opportunity_status(
    opp_id: int,
    status: str,
    *,
    next_action: str | None = None,
    next_action_priority: str | None = None,
) -> None:
    ensure_opportunity_schema()
    now = _utcnow()
    with get_conn() as conn:
        if next_action is None:
            conn.execute(
                "UPDATE opportunities SET status=?, updated_at=? WHERE id=?",
                (status, now, opp_id),
            )
        else:
            conn.execute(
                """
                UPDATE opportunities
                SET status=?, next_action=?, next_action_priority=?, updated_at=?
                WHERE id=?
                """,
                (
                    status,
                    next_action,
                    next_action_priority or "MEDIUM",
                    now,
                    opp_id,
                ),
            )


def add_opportunity_feedback(
    opportunity_id: int,
    action: str,
    *,
    reason: str = "",
    meta: dict[str, Any] | None = None,
) -> int:
    ensure_opportunity_schema()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO opportunity_feedback(opportunity_id, action, reason, ts, meta_json)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                opportunity_id,
                action,
                reason,
                _utcnow(),
                json.dumps(meta or {}, ensure_ascii=False),
            ),
        )
        return int(cur.lastrowid)


def list_opportunity_feedback(
    *,
    limit: int = 200,
    opportunity_id: int | None = None,
) -> list[sqlite3.Row]:
    ensure_opportunity_schema()
    with get_conn() as conn:
        if opportunity_id is not None:
            return conn.execute(
                """
                SELECT * FROM opportunity_feedback
                WHERE opportunity_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (opportunity_id, limit),
            ).fetchall()
        return conn.execute(
            """
            SELECT * FROM opportunity_feedback
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()


def funnel_counts() -> dict[str, int]:
    ensure_opportunity_schema()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS c
            FROM opportunities
            WHERE type = 'JOB'
            GROUP BY status
            """
        ).fetchall()
    out = {r["status"]: int(r["c"]) for r in rows}
    return out


def save_metrics_day(day: str, payload: dict[str, Any]) -> None:
    ensure_opportunity_schema()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO opportunity_metrics_daily(day, payload_json)
            VALUES(?, ?)
            ON CONFLICT(day) DO UPDATE SET payload_json=excluded.payload_json
            """,
            (day, json.dumps(payload, ensure_ascii=False)),
        )


def count_opportunities() -> int:
    ensure_opportunity_schema()
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM opportunities").fetchone()
        return int(row["c"] if row else 0)
