"""SQLite state: queue, agent_id, health, PnL, bounty drafts."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from orchestrator.config import STATE_DB


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    STATE_DB.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 0,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                processed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS health_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS finance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                action TEXT NOT NULL,
                payload TEXT NOT NULL,
                pnl_usd REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS bounty_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            );
            CREATE TABLE IF NOT EXISTS run_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                run_type TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT
            );
            """
        )


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def kv_get(key: str, default: str | None = None) -> str | None:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def kv_set(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO kv(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def enqueue_task(source: str, payload: dict[str, Any], priority: int = 0) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO task_queue(source, priority, payload, created_at) VALUES(?, ?, ?, ?)",
            (source, priority, json.dumps(payload), _utcnow()),
        )
        return int(cur.lastrowid)


def fetch_pending_tasks(limit: int = 10) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT * FROM task_queue
            WHERE status = 'pending'
            ORDER BY priority DESC, id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def mark_task_done(task_id: int, status: str = "done") -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE task_queue SET status = ?, processed_at = ? WHERE id = ?",
            (status, _utcnow(), task_id),
        )


def log_health(payload: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO health_log(ts, payload) VALUES(?, ?)",
            (_utcnow(), json.dumps(payload)),
        )


def log_run(run_type: str, status: str, summary: str = "") -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO run_log(ts, run_type, status, summary) VALUES(?, ?, ?, ?)",
            (_utcnow(), run_type, status, summary),
        )


def last_run_summary() -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT summary, ts, status FROM run_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return f"[{row['ts']}] {row['status']}: {row['summary'] or '—'}"


def add_bounty_draft(title: str, body: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO bounty_drafts(ts, title, body) VALUES(?, ?, ?)",
            (_utcnow(), title, body),
        )
        return int(cur.lastrowid)


def get_bounty_draft(draft_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM bounty_drafts WHERE id = ?", (draft_id,)
        ).fetchone()


def update_bounty_status(draft_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE bounty_drafts SET status = ? WHERE id = ?", (status, draft_id)
        )


def list_bounty_drafts(status: str | None = "pending", limit: int = 20) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if status is None:
            return conn.execute(
                """
                SELECT * FROM bounty_drafts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return conn.execute(
            """
            SELECT * FROM bounty_drafts
            WHERE status = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()


def bounty_draft_ghsa_ids() -> set[str]:
    """Collect GHSA IDs already referenced in draft titles/bodies."""
    import re

    pattern = re.compile(r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}", re.I)
    ids: set[str] = set()
    with get_conn() as conn:
        rows = conn.execute("SELECT title, body FROM bounty_drafts").fetchall()
    for row in rows:
        for text in (row["title"], row["body"]):
            ids.update(m.upper() for m in pattern.findall(text or ""))
    return ids


KV_LAST_PROGRAM_SUGGESTION = "bounty_last_program_suggestion"


def get_last_program_suggestion() -> str | None:
    return kv_get(KV_LAST_PROGRAM_SUGGESTION)


def set_last_program_suggestion(ts: str | None = None) -> None:
    kv_set(KV_LAST_PROGRAM_SUGGESTION, ts or _utcnow())


def log_finance(action: str, payload: dict[str, Any], pnl_usd: float = 0) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO finance_log(ts, action, payload, pnl_usd) VALUES(?, ?, ?, ?)",
            (_utcnow(), action, json.dumps(payload), pnl_usd),
        )


def today_pnl() -> float:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(pnl_usd), 0) AS total
            FROM finance_log
            WHERE ts LIKE ?
            """,
            (f"{today}%",),
        ).fetchone()
        return float(row["total"]) if row else 0.0


def year_pnl(year: int | None = None) -> float:
    year = year or datetime.now(timezone.utc).year
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(pnl_usd), 0) AS total
            FROM finance_log
            WHERE ts LIKE ?
            """,
            (f"{year}-%",),
        ).fetchone()
        return float(row["total"]) if row else 0.0
