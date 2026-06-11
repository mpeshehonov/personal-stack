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
from finance.executor import FinanceExecutor
from finance.proposal_parser import extract_trade_proposals
from orchestrator.config import load_env_file
from orchestrator.cursor_runner import run_ask, run_daily_agent
from orchestrator.health import collect_health, format_health
from orchestrator.memory import build_context_pack, ensure_daily_log
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


async def notify_telegram(text: str) -> None:
    load_env_file(".env.telegram")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_ids = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "")
    if not token or not chat_ids:
        logger.info("Telegram notify (no config): %s", text[:200])
        return
    import httpx

    for uid in chat_ids.split(","):
        uid = uid.strip()
        if not uid:
            continue
        try:
            await httpx.AsyncClient().post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": uid, "text": text[:4000]},
                timeout=15,
            )
        except Exception as e:
            logger.warning("Telegram notify failed: %s", e)


async def process_task(row) -> None:
    payload = json.loads(row["payload"])
    kind = payload.get("type", "task")
    text = payload.get("text", "")

    if kind == "ask":
        result = await asyncio.to_thread(run_ask, text)
        await notify_telegram(f"Ask result:\n{result[:3500]}")
    elif kind == "task":
        context = payload.get("context", text)
        health = collect_health()
        result = await asyncio.to_thread(
            run_daily_agent, context, health.light_mode
        )
        finance = FinanceExecutor()
        proposals = extract_trade_proposals(result)
        if proposals:
            outcomes = await asyncio.to_thread(
                finance.process_agent_proposals, proposals
            )
            approved = sum(1 for o in outcomes if o.get("approved"))
            await notify_telegram(
                f"Task done ({approved}/{len(outcomes)} finance proposals):\n"
                f"{result[:3200]}"
            )
        else:
            await notify_telegram(f"Task done:\n{result[:3500]}")
    mark_task_done(row["id"])


async def run_daily_cycle() -> None:
    if kv_get("autonomy_paused") == "true":
        logger.info("Autonomy paused, skipping daily cycle")
        await notify_telegram("Daily cycle skipped: autonomy paused")
        return

    health = collect_health()
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
    draft_ids = await asyncio.to_thread(daily_bounty_scan)

    report = (
        f"Daily report\n\n{format_health(health)}\n\n"
        f"Agent: {summary[:800]}\n\n"
        f"Finance: {json.dumps(fin_summary, indent=0)[:500]}\n\n"
        f"Bounty drafts: {draft_ids}"
    )
    log_run("daily", "finished", summary[:500])
    await notify_telegram(report)


async def worker_loop() -> None:
    init_db()
    logger.info("Orchestrator started")
    while True:
        if kv_get("daily_trigger") == "true":
            kv_set("daily_trigger", "false")
            try:
                await run_daily_cycle()
            except Exception as e:
                logger.exception("Daily cycle failed")
                log_run("daily", "error", str(e))
                await notify_telegram(f"Daily cycle error: {e}")

        tasks = fetch_pending_tasks(5)
        for row in tasks:
            try:
                await process_task(row)
            except Exception as e:
                logger.exception("Task %s failed", row["id"])
                mark_task_done(row["id"], "error")
                await notify_telegram(f"Task error: {e}")

        await asyncio.sleep(POLL_INTERVAL)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "daily":
        asyncio.run(run_daily_cycle())
        return
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
