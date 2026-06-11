"""Telegram bot — separate process, writes to task queue."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from finance.goal_tracker import format_goal_progress
from finance.paper_stats import format_paper_stats
from finance.polymarket_client import PolymarketClient, is_geoblocked
from orchestrator.config import load_env_file
from orchestrator.health import collect_health, format_health
from orchestrator.state import (
    get_bounty_draft,
    init_db,
    kv_get,
    kv_set,
    last_run_summary,
    enqueue_task,
    list_bounty_drafts,
    today_pnl,
    update_bounty_status,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [telegram] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _allowed_user(user) -> bool:
    load_env_file(".env.telegram")
    ids = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "")
    allowed_ids = {int(x.strip()) for x in ids.split(",") if x.strip().isdigit()}
    if allowed_ids and user.id in allowed_ids:
        return True
    names = os.environ.get("TELEGRAM_ALLOWED_USERNAMES", "")
    allowed_names = {
        x.strip().lower().lstrip("@") for x in names.split(",") if x.strip()
    }
    if allowed_names and user.username and user.username.lower() in allowed_names:
        return True
    return not (allowed_ids or allowed_names)


async def cmd_status(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    h = collect_health()
    msg = (
        f"{format_health(h)}\n\n"
        f"Last run: {last_run_summary() or 'none'}\n"
        f"PnL today: ${today_pnl():.2f}\n"
        f"{format_goal_progress()}\n"
        f"Paused: {kv_get('autonomy_paused', 'false')}"
    )
    await update.message.reply_text(msg)


async def cmd_task(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Usage: /task <description>")
        return
    tid = enqueue_task("telegram", {"type": "task", "text": text}, priority=10)
    await update.message.reply_text(f"Task #{tid} queued.")


async def cmd_ask(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Usage: /ask <question>")
        return
    tid = enqueue_task("telegram", {"type": "ask", "text": text}, priority=5)
    await update.message.reply_text(f"Ask #{tid} queued.")


async def cmd_pause(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "true")
    await update.message.reply_text("Autonomy paused.")


async def cmd_resume(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "false")
    await update.message.reply_text("Autonomy resumed.")


async def cmd_memory(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await update.message.reply_text(last_run_summary() or "No runs yet.")


def _parse_bounty_draft_id(args: list[str]) -> int | None:
    if not args:
        return None
    if args[0].lower() == "bounty" and len(args) > 1:
        return int(args[1])
    return int(args[0])


async def cmd_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    pending = list_bounty_drafts(status="pending", limit=15)
    if not pending:
        await update.message.reply_text(
            "No pending bounty drafts.\n\n"
            "Daily scans create advisory drafts and program suggestions. "
            "Use /approve bounty <id> when ready to submit manually."
        )
        return
    lines = ["Pending bounty drafts:", ""]
    for row in pending:
        title = row["title"]
        if len(title) > 70:
            title = title[:67] + "..."
        lines.append(f"#{row['id']} — {title}")
        lines.append(f"  created: {row['ts'][:19]}")
    lines.extend(
        [
            "",
            "Commands:",
            "/approve bounty <id> — mark ready for manual submission",
            "/reject bounty <id> — discard draft",
        ]
    )
    await update.message.reply_text("\n".join(lines))


async def cmd_approve_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /approve bounty <id>\n\n"
            "List pending drafts with /bounty"
        )
        return
    try:
        draft_id = _parse_bounty_draft_id(context.args)
    except (ValueError, TypeError):
        await update.message.reply_text("Invalid draft id. Usage: /approve bounty <id>")
        return
    if draft_id is None:
        await update.message.reply_text("Usage: /approve bounty <id>")
        return
    draft = get_bounty_draft(draft_id)
    if not draft:
        await update.message.reply_text(f"Draft #{draft_id} not found. Try /bounty")
        return
    if draft["status"] != "pending":
        await update.message.reply_text(
            f"Draft #{draft_id} is already '{draft['status']}'."
        )
        return
    update_bounty_status(draft_id, "approved")
    await update.message.reply_text(
        f"✅ Draft #{draft_id} approved for manual submission only.\n\n"
        f"Title: {draft['title']}\n\n"
        f"{draft['body'][:1800]}\n\n"
        "Reminder: submit only after verifying scope, impact, and repro steps. "
        "Never auto-submit from the agent."
    )


async def cmd_reject_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text("Usage: /reject bounty <id>")
        return
    try:
        draft_id = _parse_bounty_draft_id(context.args)
    except (ValueError, TypeError):
        await update.message.reply_text("Invalid draft id. Usage: /reject bounty <id>")
        return
    if draft_id is None:
        await update.message.reply_text("Usage: /reject bounty <id>")
        return
    draft = get_bounty_draft(draft_id)
    if not draft:
        await update.message.reply_text(f"Draft #{draft_id} not found.")
        return
    update_bounty_status(draft_id, "rejected")
    await update.message.reply_text(f"Draft #{draft_id} rejected.")


async def cmd_finance(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    poly = PolymarketClient()
    geoblock = poly.check_geoblock()
    if is_geoblocked(geoblock):
        geo_line = "Geoblock: BLOCKED (live orders disabled)"
    elif geoblock.get("error"):
        geo_line = f"Geoblock: unknown ({geoblock['error']})"
    else:
        geo_line = "Geoblock: OK"
    msg = (
        f"{geo_line}\n\n"
        f"{format_paper_stats()}\n\n"
        f"{format_goal_progress()}"
    )
    await update.message.reply_text(msg)


async def cmd_help(update, context) -> None:
    await update.message.reply_text(
        "/status — server health\n"
        "/finance — geoblock, paper trades, goal\n"
        "/task <text> — queue task\n"
        "/ask <text> — quick agent question\n"
        "/pause / /resume — autonomy control\n"
        "/memory — last run summary\n"
        "/bounty — list pending bounty drafts\n"
        "/approve bounty <id> — approve draft for manual submission\n"
        "/reject bounty <id> — reject bounty draft"
    )


def main() -> None:
    load_env_file(".env.telegram")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token.startswith("123456") or "..." in token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN not configured — edit secrets/.env.telegram and restart"
        )
        import time

        while True:
            time.sleep(3600)

    init_db()

    from telegram.ext import Application, CommandHandler

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("finance", cmd_finance))
    app.add_handler(CommandHandler("task", cmd_task))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("bounty", cmd_bounty))
    app.add_handler(CommandHandler("approve", cmd_approve_bounty))
    app.add_handler(CommandHandler("reject", cmd_reject_bounty))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))

    logger.info("Telegram bot starting")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
