"""Long-running orchestrator worker: task queue + daily runs."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Ensure agent package root on path
AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from bounty.scanner import daily_bounty_scan
from job_hunt.scanner import daily_job_scan
from finance.executor import FinanceExecutor
from finance.proposal_parser import extract_trade_proposals
from orchestrator.cursor_runner import run_ask, run_daily_agent, run_task
from orchestrator.git_deploy import apply_daily_commit, apply_task_deploy, pull_latest
from orchestrator.daily_report import format_daily_report_rich
from orchestrator.daily_validator import validate_daily_log
from orchestrator.format_ru import run_status_ru
from orchestrator.health import collect_health
from orchestrator.memory import build_context_pack, ensure_daily_log
from telegram_bot.rich_send import notify_allowed_users
from orchestrator.state import (
    fetch_pending_tasks,
    init_db,
    kv_get,
    kv_set,
    log_health,
    log_run,
    mark_task_done,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [orchestrator] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL = int(os.environ.get("ORCHESTRATOR_POLL_SEC", "30"))


async def process_task(row) -> None:
    payload = json.loads(row["payload"])
    kind = payload.get("type", "task")
    text = payload.get("text", "")

    if kind == "ask":
        result = await asyncio.to_thread(run_ask, text)
        await notify_allowed_users(f"# Ask result\n\n{result}")
    elif kind == "task":
        ok, sync_msg = await asyncio.to_thread(pull_latest)
        if not ok:
            await notify_allowed_users(
                f"# Задача отменена\n\nРепозиторий не синхронизирован.\n\n{sync_msg}"
            )
            mark_task_done(row["id"])
            return
        result = await asyncio.to_thread(run_task, text)
        deploy_report = await asyncio.to_thread(apply_task_deploy, result)
        finance = FinanceExecutor()
        proposals = extract_trade_proposals(result)
        if proposals:
            outcomes = await asyncio.to_thread(
                finance.process_agent_proposals, proposals
            )
            approved = sum(1 for o in outcomes if o.get("approved"))
            await notify_allowed_users(
                f"# Задача выполнена\n\n"
                f"Finance proposals: {approved}/{len(outcomes)}\n\n"
                f"{result}\n\n## Deploy\n\n{deploy_report}"
            )
        else:
            await notify_allowed_users(
                f"# Задача выполнена\n\n{result}\n\n## Deploy\n\n{deploy_report}"
            )
    mark_task_done(row["id"])


async def run_daily_cycle() -> None:
    if kv_get("autonomy_paused") == "true":
        logger.info("Autonomy paused, skipping daily cycle")
        await notify_allowed_users("## Ежедневный цикл\n\nПропущен: автономия на паузе.")
        return

    summary = ""
    health = collect_health()
    fin_summary: dict = {}
    draft_ids: list[int] = []
    bounty_summary: dict = {}
    job_summary: dict | None = None
    status = "finished"
    try:
        log_health(health.to_dict())
        ensure_daily_log()

        if not health.site_ok:
            logger.warning("Site down — attempting redeploy")
            import subprocess

            subprocess.run(
                [str(AGENT_ROOT.parent / "scripts" / "redeploy-site.sh")],
                check=False,
            )
            health = collect_health()

        context = build_context_pack(health)
        summary = await asyncio.to_thread(run_daily_agent, context, health.light_mode)

        log_ok, log_warnings = await asyncio.to_thread(validate_daily_log)
        if log_warnings:
            logger.info("Daily log validation: %s", "; ".join(log_warnings[:5]))
            summary = summary + "\n\n[Validator] " + "; ".join(log_warnings[:3])

        finance = FinanceExecutor()
        agent_proposals = extract_trade_proposals(summary)
        proposal_outcomes: list[dict] = []
        if agent_proposals:
            proposal_outcomes = await asyncio.to_thread(
                finance.process_agent_proposals, agent_proposals
            )
        fin_summary = await asyncio.to_thread(finance.daily_analysis)
        if proposal_outcomes:
            fin_summary["agent_proposals"] = proposal_outcomes
        bounty_result = await asyncio.to_thread(daily_bounty_scan)
        bounty_summary = bounty_result.to_dict()
        draft_ids = bounty_summary.get("draft_ids") or []
        job_summary = await asyncio.to_thread(daily_job_scan)

        log_run("daily", "finished", summary[:12000])
    except Exception as e:
        logger.exception("Daily cycle failed")
        status = "error"
        summary = summary or f"Ошибка daily-цикла: {e}"
        log_run("daily", "error", summary[:12000])
    finally:
        commit_report = await asyncio.to_thread(apply_daily_commit, summary)
        try:
            report_md = format_daily_report_rich(
                health=health,
                summary=summary,
                fin_summary=fin_summary,
                bounty_summary=bounty_summary,
                job_summary=job_summary,
                commit_report=commit_report,
                status=status,
            )
            await notify_allowed_users(report_md)
        except Exception as e:
            logger.exception("Daily report notify failed")
            await notify_allowed_users(
                f"# Ежедневный отчёт\n\n**Статус:** {run_status_ru(status)}\n\n"
                f"Не удалось сформировать полный отчёт: `{e}`\n\n"
                f"**Git:** {commit_report}\n\n**Агент:** {(summary or '—')[:800]}"
            )


async def worker_loop() -> None:
    init_db()
    from orchestrator.cursor_session import cleanup_stale_bridges_on_startup

    cleanup_stale_bridges_on_startup()
    logger.info("Orchestrator started")
    while True:
        if kv_get("daily_trigger") == "true":
            kv_set("daily_trigger", "false")
            await run_daily_cycle()

        tasks = fetch_pending_tasks(5)
        for row in tasks:
            try:
                await process_task(row)
            except Exception as e:
                logger.exception("Task %s failed", row["id"])
                mark_task_done(row["id"], "error")
                await notify_allowed_users(f"# Task error\n\n`{e}`")

        await asyncio.sleep(POLL_INTERVAL)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "daily":
        asyncio.run(run_daily_cycle())
        return
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
