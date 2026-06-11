"""Telegram bot — Russian UI, streaming /ask, task queue."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import time
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from finance.goal_tracker import goal_progress
from finance.paper_stats import paper_trade_stats
from finance.polymarket_client import PolymarketClient, is_geoblocked
from orchestrator.config import load_env_file
from orchestrator.cursor_runner import run_ask_streaming
from orchestrator.format_ru import (
    format_date_ru,
    format_last_run,
    format_load,
    format_percent,
    format_usd,
)
from orchestrator.health import collect_health
from orchestrator.state import (
    get_bounty_draft,
    get_last_run,
    init_db,
    kv_get,
    kv_set,
    enqueue_task,
    list_bounty_drafts,
    today_pnl,
    update_bounty_status,
)
from telegram_bot.streaming import AnswerStreamer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [telegram] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    ("start", "Начало и список команд"),
    ("help", "Справка по командам"),
    ("status", "Состояние сервера"),
    ("finance", "Финансы и paper-торговля"),
    ("ask", "Вопрос агенту (стриминг ответа)"),
    ("task", "Поставить задачу в очередь"),
    ("bounty", "Черновики bug bounty"),
    ("memory", "Итог последнего daily-цикла"),
    ("pause", "Приостановить автономию"),
    ("resume", "Возобновить автономию"),
]


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


def _format_health_ru(h) -> str:
    return (
        f"CPU: {format_percent(h.cpu_percent)} | RAM: {format_percent(h.memory_percent)} "
        f"({h.memory_available_mb:.0f} МБ свободно)\n"
        f"Диск: {format_percent(h.disk_percent)} | Нагрузка: {format_load(h.load_avg)}\n"
        f"Сайт: {'OK' if h.site_ok else 'НЕДОСТУПЕН'} | "
        f"Docker: {'OK' if h.docker_ok else 'ПРОБЛЕМА'}\n"
        f"Режим: {'лёгкий' if h.light_mode else 'полный'}"
    )


def _format_last_run_ru() -> str:
    run = get_last_run()
    if not run:
        return "ещё не было"
    return format_last_run(run["ts"], run["status"], run["summary"])


def _format_goal_ru() -> str:
    p = goal_progress()
    pct = (
        f"{int(p['progress_pct'])}%"
        if p["progress_pct"] == round(p["progress_pct"])
        else f"{p['progress_pct']:.1f}%"
    )
    return (
        f"Цель {format_usd(p['target_usd'])} к {format_date_ru(p['deadline'])}: "
        f"заработано {format_usd(p['earned_usd'])} ({pct}), "
        f"осталось {format_usd(p['remaining_usd'])}, "
        f"~{format_usd(p['daily_needed_usd'])}/день, {p['days_left']} дн."
    )


def _format_paper_ru() -> str:
    stats = paper_trade_stats()
    if stats["count"] == 0:
        return "Paper-сделок пока нет."
    lines = [
        f"Paper-сделки: {stats['count']} (${stats['total_usd']:,.2f} всего)",
    ]
    if stats["by_side"]:
        side_parts = [f"{k}={v}" for k, v in sorted(stats["by_side"].items())]
        lines.append(f"Стороны: {', '.join(side_parts)}")
    for t in stats["recent"]:
        title = t.get("market_title") or t["market_id"][:12]
        if len(title) > 48:
            title = title[:45] + "..."
        lines.append(f"• {t['side']} ${t['size_usd']:.0f} — {title}")
    return "\n".join(lines)


def _help_text() -> str:
    return (
        "Команды бота:\n\n"
        "/status — состояние сервера и сервисов\n"
        "/finance — geoblock, paper-сделки, цель $15k\n"
        "/ask <вопрос> — ответ агента со стримингом\n"
        "/task <текст> — задача в очередь orchestrator\n"
        "/bounty — черновики bug bounty\n"
        "/approve bounty <id> — одобрить черновик\n"
        "/reject bounty <id> — отклонить черновик\n"
        "/memory — итог последнего daily-цикла\n"
        "/pause — приостановить автономию\n"
        "/resume — возобновить автономию\n"
        "/help — эта справка"
    )


async def cmd_status(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    h = collect_health()
    paused = kv_get("autonomy_paused", "false") == "true"
    msg = (
        f"{_format_health_ru(h)}\n\n"
        f"Последний запуск: {_format_last_run_ru()}\n"
        f"PnL сегодня: {format_usd(today_pnl())}\n"
        f"{_format_goal_ru()}\n"
        f"Автономия: {'пауза' if paused else 'активна'}"
    )
    await update.message.reply_text(msg)


async def cmd_task(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Использование: /task <описание задачи>")
        return
    tid = enqueue_task("telegram", {"type": "task", "text": text}, priority=10)
    await update.message.reply_text(
        f"Задача #{tid} поставлена в очередь. Результат придёт в этот чат."
    )


async def cmd_ask(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Использование: /ask <вопрос>")
        return

    chat_id = update.effective_chat.id
    draft_id = int((update.message.message_id * 997 + int(time.time() * 1000)) % 2_000_000_000) or 1
    streamer = AnswerStreamer(context.bot, chat_id, draft_id)

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def on_chunk(accumulated: str) -> None:
        asyncio.run_coroutine_threadsafe(queue.put(("chunk", accumulated)), loop)

    def worker() -> None:
        try:
            result = run_ask_streaming(text, on_chunk)
            asyncio.run_coroutine_threadsafe(queue.put(("done", result)), loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(queue.put(("error", str(e))), loop)

    threading.Thread(target=worker, daemon=True).start()

    last_text = ""
    try:
        while True:
            kind, payload = await queue.get()
            if kind == "chunk":
                if payload and payload != last_text:
                    await streamer.update(payload)
                    last_text = payload
            elif kind == "done":
                await streamer.finalize(payload or last_text)
                break
            elif kind == "error":
                await streamer.finalize(f"Ошибка: {payload}")
                break
    except Exception as e:
        logger.exception("cmd_ask streaming failed")
        await streamer.finalize(f"Ошибка бота: {e}")


async def cmd_pause(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "true")
    await update.message.reply_text("Автономия приостановлена. Daily-циклы пропускаются.")


async def cmd_resume(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "false")
    await update.message.reply_text("Автономия возобновлена.")


async def cmd_memory(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await update.message.reply_text(_format_last_run_ru())


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
            "Нет ожидающих черновиков.\n\n"
            "Ежедневный скан создаёт advisory-черновики и подсказки программ. "
            "Одобряй вручную: /approve bounty <id>"
        )
        return
    lines = ["Ожидающие черновики bug bounty:", ""]
    for row in pending:
        title = row["title"]
        if len(title) > 70:
            title = title[:67] + "..."
        lines.append(f"#{row['id']} — {title}")
        lines.append(f"  создан: {row['ts'][:19]}")
    lines.extend(
        [
            "",
            "/approve bounty <id> — готов к ручной отправке",
            "/reject bounty <id> — отклонить",
        ]
    )
    await update.message.reply_text("\n".join(lines))


async def cmd_approve_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text(
            "Использование: /approve bounty <id>\n\nСписок: /bounty"
        )
        return
    try:
        draft_id = _parse_bounty_draft_id(context.args)
    except (ValueError, TypeError):
        await update.message.reply_text("Неверный id. Пример: /approve bounty 3")
        return
    if draft_id is None:
        await update.message.reply_text("Использование: /approve bounty <id>")
        return
    draft = get_bounty_draft(draft_id)
    if not draft:
        await update.message.reply_text(f"Черновик #{draft_id} не найден. См. /bounty")
        return
    if draft["status"] != "pending":
        await update.message.reply_text(f"Черновик #{draft_id} уже в статусе «{draft['status']}».")
        return
    update_bounty_status(draft_id, "approved")
    await update.message.reply_text(
        f"Черновик #{draft_id} одобрен для ручной отправки.\n\n"
        f"Заголовок: {draft['title']}\n\n"
        f"{draft['body'][:1800]}\n\n"
        "Отправляй только после проверки scope, impact и шагов воспроизведения. "
        "Авто-submit из агента отключён."
    )


async def cmd_reject_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text("Использование: /reject bounty <id>")
        return
    try:
        draft_id = _parse_bounty_draft_id(context.args)
    except (ValueError, TypeError):
        await update.message.reply_text("Неверный id. Пример: /reject bounty 3")
        return
    if draft_id is None:
        await update.message.reply_text("Использование: /reject bounty <id>")
        return
    draft = get_bounty_draft(draft_id)
    if not draft:
        await update.message.reply_text(f"Черновик #{draft_id} не найден.")
        return
    update_bounty_status(draft_id, "rejected")
    await update.message.reply_text(f"Черновик #{draft_id} отклонён.")


async def cmd_finance(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    poly = PolymarketClient()
    geoblock = poly.check_geoblock()
    if is_geoblocked(geoblock):
        geo_line = "Geoblock: ЗАБЛОКИРОВАН (live-ордера отключены)"
    elif geoblock.get("error"):
        geo_line = f"Geoblock: неизвестно ({geoblock['error']})"
    else:
        geo_line = "Geoblock: OK"
    msg = (
        f"{geo_line}\n\n"
        f"{_format_paper_ru()}\n\n"
        f"{_format_goal_ru()}"
    )
    await update.message.reply_text(msg)


async def cmd_help(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await update.message.reply_text(_help_text())


async def post_init(app) -> None:
    from telegram import BotCommand

    commands = [BotCommand(cmd, desc) for cmd, desc in BOT_COMMANDS]
    await app.bot.set_my_commands(commands)
    try:
        await app.bot.set_my_description(
            "Персональный агент: сервер, финансы, bug bounty, задачи Cursor."
        )
        await app.bot.set_my_short_description(
            "Автономный агент на VPS. /ask — вопрос со стримингом."
        )
    except Exception as e:
        logger.info("setMyDescription skipped: %s", e)
    logger.info("Команды бота зарегистрированы (%d)", len(commands))


def main() -> None:
    load_env_file(".env.telegram")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token.startswith("123456") or "..." in token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN не настроен — secrets/.env.telegram и restart"
        )
        import time

        while True:
            time.sleep(3600)

    init_db()

    from telegram.ext import Application, CommandHandler

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )
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

    logger.info("Telegram-бот запускается")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
