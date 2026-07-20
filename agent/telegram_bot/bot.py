"""Telegram bot — Russian UI, streaming /ask, task queue."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from finance.goal_tracker import goal_progress, milestone_progress
from finance.paper_stats import paper_trade_stats
from finance.polymarket_client import PolymarketClient, is_geoblocked
from orchestrator.config import load_env_file
from orchestrator.cursor_runner import run_ask_streaming, run_task_streaming
from orchestrator.git_deploy import apply_task_deploy, pull_latest
from orchestrator.format_ru import (
    format_date_ru,
    format_datetime_ru,
    format_last_run,
    format_load,
    format_percent,
    format_usd,
    run_status_ru,
)
from orchestrator.cursor_session import cursor_holder
from orchestrator.health import collect_health
from orchestrator.memory import get_latest_daily_log
from orchestrator.state import (
    add_job_application,
    get_bounty_draft,
    get_bounty_draft_meta,
    get_job_lead,
    get_last_daily_run,
    get_last_run,
    init_db,
    kv_get,
    kv_set,
    list_bounty_drafts,
    list_job_leads,
    today_pnl,
    update_bounty_draft_meta,
    update_bounty_status,
)
from bounty.config import BOUNTY_AUTO_SUBMIT, BOUNTY_ENABLED
from bounty.models import BountyFinding
from bounty.scanner import manual_bounty_research, purge_bounty_queue
from bounty.submit import hackerone_configured, submit_finding
from job_hunt.config import JOBHUNT_ENABLED, JOBHUNT_MIN_MATCH
from job_hunt.drafter import draft_cover_letter, format_draft_markdown
from job_hunt.resume_sync import apply_sync, format_auth_markdown, format_sync_plan_markdown
from job_hunt.scanner import scan_and_store_leads
from telegram_bot.background import job_running, list_running_jobs, start_background_job
from telegram_bot.rich_send import reply_rich, send_rich_markdown
from telegram_bot.streaming import AnswerStreamer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [telegram] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Один активный запрос на чат (/ask или /task)
_chat_locks: dict[int, asyncio.Lock] = {}

FINALIZE_TIMEOUT_SEC = 120
DEPLOY_TIMEOUT_SEC = 900


def _chat_lock(chat_id: int) -> asyncio.Lock:
    if chat_id not in _chat_locks:
        _chat_locks[chat_id] = asyncio.Lock()
    return _chat_locks[chat_id]

BOT_COMMANDS = [
    ("start", "Начало и список команд"),
    ("help", "Справка по командам"),
    ("status", "Состояние сервера"),
    ("ask", "Вопрос агенту (только ответ, без правок)"),
    ("task", "Задача: правки + commit + deploy"),
    ("jobs", "Вакансии и feedback"),
    ("sources", "Веса источников вакансий"),
    ("cover", "Сопровод к вакансии"),
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


def _format_status_rich(h) -> str:
    paused = kv_get("autonomy_paused", "false") == "true"
    run = get_last_run()
    last_run = (
        format_last_run(run["ts"], run["status"], run["summary"], preview_len=120)
        if run
        else "ещё не было"
    )
    return f"""# Статус сервера

| Метрика | Значение |
|:--------|:---------|
| CPU | {format_percent(h.cpu_percent)} |
| RAM | {format_percent(h.memory_percent)} ({h.memory_available_mb:.0f} МБ свободно) |
| Диск | {format_percent(h.disk_percent)} |
| Нагрузка | {format_load(h.load_avg)} |
| Сайт | {'**OK**' if h.site_ok else '**НЕДОСТУПЕН**'} |
| Docker | {'**OK**' if h.docker_ok else '**ПРОБЛЕМА**'} |
| Режим | {'лёгкий' if h.light_mode else 'полный'} |
| Автономия | {'пауза' if paused else 'активна'} |

**Последний запуск:** {last_run}

**PnL сегодня:** {format_usd(today_pnl())}

## Цели

{_format_goal_ru()}
"""


def _format_goal_ru() -> str:
    p = goal_progress()
    m = milestone_progress()
    pct = (
        f"{int(p['progress_pct'])}%"
        if p["progress_pct"] == round(p["progress_pct"])
        else f"{p['progress_pct']:.1f}%"
    )
    m_pct = (
        f"{int(m['progress_pct'])}%"
        if m["progress_pct"] == round(m["progress_pct"])
        else f"{m['progress_pct']:.1f}%"
    )
    return (
        f"- **M1 ({m['label']}):** {format_usd(m['earned_usd'])} / {format_usd(m['target_usd'])} "
        f"({m_pct}) к {format_date_ru(m['deadline'])}\n"
        f"- **Год:** {format_usd(p['target_usd'])} к {format_date_ru(p['deadline'])} — "
        f"заработано {format_usd(p['earned_usd'])} ({pct}), "
        f"осталось {format_usd(p['remaining_usd'])}, "
        f"~{format_usd(p['daily_needed_usd'])}/день, {p['days_left']} дн."
    )


def _format_paper_ru() -> str:
    stats = paper_trade_stats()
    if stats["count"] == 0:
        return "_Paper-сделок пока нет._"
    lines = [
        f"**Paper-сделки:** {stats['count']} (${stats['total_usd']:,.2f} всего)",
    ]
    if stats["by_side"]:
        side_parts = [f"{k}={v}" for k, v in sorted(stats["by_side"].items())]
        lines.append(f"**Стороны:** {', '.join(side_parts)}")
    for t in stats["recent"]:
        title = t.get("market_title") or t["market_id"][:12]
        if len(title) > 48:
            title = title[:45] + "..."
        lines.append(f"- {t['side']} ${t['size_usd']:.0f} — {title}")
    return "\n".join(lines)


def _format_finance_rich() -> str:
    poly = PolymarketClient()
    geoblock = poly.check_geoblock()
    if is_geoblocked(geoblock):
        geo_line = "**Geoblock:** ЗАБЛОКИРОВАН (live-ордера отключены)"
    elif geoblock.get("error"):
        geo_line = f"**Geoblock:** неизвестно ({geoblock['error']})"
    else:
        geo_line = "**Geoblock:** OK"
    return f"""# Финансы

{geo_line}

## Paper

{_format_paper_ru()}

## Цели

{_format_goal_ru()}
"""


def _format_memory_rich() -> str:
    run = get_last_daily_run()
    log_body = get_latest_daily_log()
    parts = ["# Итог последнего daily-цикла", ""]
    if run:
        parts.append(f"**Время:** {format_datetime_ru(run['ts'])}")
        parts.append(f"**Статус:** {run_status_ru(run['status'])}")
        parts.append("")
    if log_body:
        parts.append(log_body)
    elif run and run.get("summary"):
        parts.append(run["summary"])
    else:
        parts.append("_Daily-цикл ещё не выполнялся._")
    return "\n".join(parts)


def _help_text() -> str:
    return (
        "Команды бота:\n\n"
        "/status — сервер и health\n"
        "/ask — вопрос агенту (без правок)\n"
        "/task — задача: правки + commit + deploy\n"
        "/jobs — топ вакансий (career hunter)\n"
        "/jobs scan — поиск новых вакансий (фон)\n"
        "/jobs like <id> — хороший лид (учит источник)\n"
        "/jobs dislike <id> [причина] — плохой лид\n"
        "/jobs hh-digest — текст для ручной вставки в HH\n"
        "/jobs auth — проверка Habr/LinkedIn\n"
        "/jobs sync — diff резюме site → площадки\n"
        "/sources — веса и статусы источников\n"
        "/cover <id> — сопровод для лида\n"
        "/approve source <key> — включить seed-источник\n"
        "/reject source <key> — отклонить источник\n"
        "/approve resume hh|habr|all — sync резюме\n"
        "/memory — итог daily\n"
        "/pause /resume — автономия\n"
        "/help — эта справка\n\n"
        "Income/bounty paused. Фокус: сильные вакансии и проекты."
    )


async def cmd_status(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    h = await asyncio.to_thread(collect_health)
    body = _format_status_rich(h)
    holder = cursor_holder()
    if holder:
        body += f"\n\n**Cursor агент:** занят `{holder}`"
    running = list_running_jobs()
    if running:
        body += "\n\n## Фоновые задачи\n\n" + ", ".join(f"`{n}`" for n in running)
    await reply_rich(update, body)


async def _run_streaming(
    update,
    context,
    text: str,
    *,
    mode: str,
) -> None:
    chat_id = update.effective_chat.id
    lock = _chat_lock(chat_id)
    if lock.locked():
        await update.message.reply_text(
            "Подождите — ещё обрабатывается предыдущий запрос (/ask или /task)."
        )
        return

    async with lock:
        if mode == "task":
            ok, sync_msg = await asyncio.to_thread(pull_latest)
            if not ok:
                await update.message.reply_text(
                    f"Не могу начать задачу: репозиторий не синхронизирован.\n\n{sync_msg[:3500]}\n\n"
                    "Сначала закоммить или откати локальные правки на сервере."
                )
                return

        streamer = AnswerStreamer(context.bot, chat_id)
        await streamer.start()

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue()
        typing_stop = asyncio.Event()

        async def _typing_loop() -> None:
            from telegram.constants import ChatAction

            while not typing_stop.is_set():
                try:
                    await context.bot.send_chat_action(
                        chat_id=chat_id,
                        action=ChatAction.TYPING,
                    )
                except Exception:
                    pass
                try:
                    await asyncio.wait_for(typing_stop.wait(), timeout=4.0)
                    break
                except asyncio.TimeoutError:
                    pass

        typing_task = asyncio.create_task(_typing_loop())

        runner = run_ask_streaming if mode == "ask" else run_task_streaming

        def on_chunk(accumulated: str) -> None:
            asyncio.run_coroutine_threadsafe(queue.put(("chunk", accumulated)), loop)

        def worker() -> None:
            try:
                result = runner(text, on_chunk)
                asyncio.run_coroutine_threadsafe(queue.put(("done", result)), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(queue.put(("error", str(e))), loop)

        threading.Thread(target=worker, daemon=True).start()

        last_text = ""
        result_text = ""
        try:
            while True:
                kind, payload = await queue.get()
                if kind == "chunk":
                    if payload and payload != last_text:
                        await streamer.update(payload)
                        last_text = payload
                elif kind == "done":
                    result_text = payload or last_text
                    try:
                        await asyncio.wait_for(
                            streamer.finalize(result_text),
                            timeout=FINALIZE_TIMEOUT_SEC,
                        )
                    except asyncio.TimeoutError:
                        logger.error("finalize timeout chat=%s mode=%s", chat_id, mode)
                        await streamer.finalize(
                            (result_text or "Ответ получен, но финализация сообщения "
                             "превысила лимит времени. Проверь /status.")
                        )
                    break
                elif kind == "error":
                    await streamer.finalize(f"Ошибка: {payload}")
                    return
        except Exception as e:
            logger.exception("streaming failed mode=%s", mode)
            await streamer.finalize(f"Ошибка бота: {e}")
            return
        finally:
            typing_stop.set()
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass

    if mode == "task" and result_text:
        try:
            deploy_msg = await asyncio.wait_for(
                asyncio.to_thread(apply_task_deploy, result_text),
                timeout=DEPLOY_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            deploy_msg = (
                f"Deploy превысил {DEPLOY_TIMEOUT_SEC // 60} мин. "
                "Проверь логи на сервере: `journalctl -u telegram-bot -n 50`"
            )
        await send_rich_markdown(
            context.bot,
            chat_id=chat_id,
            markdown=f"## Deploy\n\n{deploy_msg}",
        )


async def cmd_task(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Использование: /task <что сделать>")
        return
    await _run_streaming(update, context, text, mode="task")


async def cmd_ask(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Использование: /ask <вопрос>")
        return
    await _run_streaming(update, context, text, mode="ask")


async def cmd_pause(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "true")
    await reply_rich(update, "## Автономия\n\nПриостановлена. Daily-циклы пропускаются.")


async def cmd_resume(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    kv_set("autonomy_paused", "false")
    await reply_rich(update, "## Автономия\n\nВозобновлена.")


async def cmd_memory(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await reply_rich(update, _format_memory_rich())


def _parse_bounty_draft_id(args: list[str]) -> int | None:
    if not args:
        return None
    if args[0].lower() == "bounty" and len(args) > 1:
        return int(args[1])
    return int(args[0])


async def cmd_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return

    if context.args and context.args[0].lower() == "test":
        from bounty.submit import verify_hackerone_auth

        ok, msg = await asyncio.to_thread(verify_hackerone_auth)
        status = "OK" if ok else "FAIL"
        await reply_rich(
            update,
            f"## HackerOne API test\n\n**{status}:** {msg}\n\n"
            "Personal token: username = handle `mpeshekhonov`, password = token.\n"
            "Страница: https://hackerone.com/settings/api_token/edit",
        )
        return

    if context.args and context.args[0].lower() == "purge":
        result = await asyncio.to_thread(purge_bounty_queue)
        await reply_rich(update, f"## Bounty purge\n\n{result.message}")
        return

    if context.args and context.args[0].lower() == "hunt":
        if not BOUNTY_ENABLED:
            await update.message.reply_text("Bounty отключён (BOUNTY_ENABLED=false).")
            return
        if job_running("bounty_hunt"):
            await update.message.reply_text(
                "Bounty hunt уже идёт в фоне. /status — другие команды работают."
            )
            return

        chat_id = update.effective_chat.id
        bot = context.bot

        async def _run_hunt() -> None:
            result = await asyncio.to_thread(manual_bounty_research)
            parts = [result.message or "Готово."]
            if result.purged_ids:
                parts.insert(0, f"Отсеяно: {', '.join(f'#{i}' for i in result.purged_ids)}")
            if result.draft_ids:
                parts.append(f"Submit-ready: {', '.join(f'#{i}' for i in result.draft_ids)}")
            await send_rich_markdown(
                bot,
                chat_id=chat_id,
                markdown="## Bounty hunt — готово\n\n" + "\n\n".join(parts),
            )

        ok, msg = start_background_job("bounty_hunt", chat_id, _run_hunt)
        await update.message.reply_text(
            f"{msg}\n\n4 фазы: scope → recon → hunt → report (curl + tools).\n"
            "30–90 мин. /status — фоновые задачи; /ask — когда Cursor свободен."
        )
        return

    pending = list_bounty_drafts(status="pending", limit=15)
    auto_note = (
        "После `/approve bounty <id>` отчёт **автоматически отправится** на HackerOne."
        if BOUNTY_AUTO_SUBMIT and hackerone_configured()
        else "Настрой `secrets/.env.bounty` для авто-сабмита на HackerOne."
    )
    if not pending:
        await reply_rich(
            update,
            "## Bug bounty (semi-auto)\n\n"
            "Нет ожидающих отчётов.\n\n"
            "Deep research + auto-QA + reviewer. Только submit-ready.\n"
            "Принудительно: `/bounty hunt` · отсев: `/bounty purge`\n\n"
            f"{auto_note}",
        )
        return
    lines = ["# Bug bounty", "", "**Готовые отчёты (pending):**", ""]
    for row in pending:
        title = row["title"]
        if len(title) > 70:
            title = title[:67] + "..."
        meta = get_bounty_draft_meta(int(row["id"]))
        sev = meta.get("severity", "?")
        score = meta.get("quality_score", "—")
        program = meta.get("program_name", "?")
        lines.append(f"- **#{row['id']}** — {title}")
        lines.append(
            f"  _{program}, {sev}, QA {score}, создан: {row['ts'][:19]}_"
        )
    lines.extend(
        [
            "",
            "`/approve bounty <id>` — одобрить и отправить",
            "`/reject bounty <id>` — отклонить",
            "",
            auto_note,
        ]
    )
    await reply_rich(update, "\n".join(lines))


def _format_jobs_rich() -> str:
    if not JOBHUNT_ENABLED:
        return (
            "## Job hunt\n\n"
            "Модуль отключён (JOBHUNT_ENABLED=false).\n\n"
            "Скопируй secrets/.env.jobhunt.template → secrets/.env.jobhunt."
        )

    leads = list_job_leads(status="new", limit=10, min_score=JOBHUNT_MIN_MATCH)
    liked = list_job_leads(status="liked", limit=5, min_score=0)
    if not leads and not liked:
        return (
            "## Job hunt\n\n"
            f"Нет новых лидов с score ≥ {JOBHUNT_MIN_MATCH}.\n\n"
            "Скан: /jobs scan. Feedback: /jobs like <id> или /jobs dislike <id>."
        )

    lines = [
        "# Job hunt",
        "",
        f"Новые лиды (score ≥ {JOBHUNT_MIN_MATCH}):",
        "",
    ]
    for row in leads:
        title = row["title"]
        if len(title) > 60:
            title = title[:57] + "..."
        company = row["company"] or "—"
        lines.append(
            f"- #{row['id']} ({row['match_score']}) {company}: {title}"
        )
        if row["url"]:
            lines.append(f"  {row['url']}")

    if liked:
        lines.extend(["", "Понравившиеся:"])
        for row in liked:
            lines.append(f"- #{row['id']} {row['company']}: {row['title'][:50]}")

    lines.extend(
        [
            "",
            "/jobs scan — новый поиск",
            "/jobs like <id> — хороший лид",
            "/jobs dislike <id> — плохой лид",
            "/cover <id> — сопровод",
            "/sources — веса источников",
        ]
    )
    return "\n".join(lines)


def _lead_row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


async def cmd_jobs(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return

    if context.args and context.args[0].lower() in ("hh-digest", "hhdigest"):
        from job_hunt.hh_digest import format_hh_digest_markdown

        md = await asyncio.to_thread(format_hh_digest_markdown)
        await reply_rich(update, md)
        return

    if context.args and context.args[0].lower() == "auth":
        md = await asyncio.to_thread(format_auth_markdown)
        await reply_rich(update, md)
        return

    if context.args and context.args[0].lower() == "sync":
        md = await asyncio.to_thread(format_sync_plan_markdown)
        await reply_rich(update, md)
        return

    if context.args and context.args[0].lower() in ("like", "dislike"):
        action = context.args[0].lower()
        if len(context.args) < 2:
            await update.message.reply_text(f"Использование: /jobs {action} <id>")
            return
        try:
            lead_id = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Неверный id. Пример: /jobs like 12")
            return
        note = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        from job_hunt.sources import apply_feedback

        try:
            result = await asyncio.to_thread(apply_feedback, lead_id, action, note=note)
        except KeyError:
            await update.message.reply_text(f"Лид #{lead_id} не найден.")
            return
        except ValueError as e:
            await update.message.reply_text(str(e))
            return

        lines = [
            f"{action} по #{result['lead_id']}: {result['company']} — {result['title'][:60]}",
            f"Источник {result['source_key']}: вес {result['weight_before']} → {result['weight_after']}",
        ]
        if result.get("disabled"):
            lines.append("Источник отключён из-за низкого веса.")
        await update.message.reply_text("\n".join(lines))
        return

    if context.args and context.args[0].lower() == "scan":
        if not JOBHUNT_ENABLED:
            await update.message.reply_text(
                "Job hunt отключён. Скопируй secrets/.env.jobhunt.template → secrets/.env.jobhunt"
            )
            return
        if job_running("job_scan"):
            await update.message.reply_text(
                "Скан вакансий уже идёт. /status — фоновые задачи."
            )
            return

        chat_id = update.effective_chat.id
        bot = context.bot

        async def _run_scan() -> None:
            summary = await asyncio.to_thread(scan_and_store_leads)
            by_source = summary.get("by_source") or {}
            source_line = ", ".join(
                f"{src} {count}" for src, count in by_source.items() if count
            ) or "—"
            parts = [
                f"Просмотрено: {summary.get('fetched', 0)} ({source_line})",
                f"Новых лидов: {summary.get('new_count', 0)}",
                f"Ниже порога: {summary.get('below_threshold', 0)}, "
                f"уже в базе: {summary.get('skipped_existing', 0)}, "
                f"дубли: {summary.get('skipped_duplicates', 0)}",
            ]
            top = summary.get("top_leads") or []
            if top:
                parts.append("")
                parts.append("Топ новых:")
                for lead in top[:5]:
                    parts.append(
                        f"- #{lead['id']} ({lead['score']}) {lead['company']}: {lead['title'][:50]}"
                    )
            snippet = summary.get("sources_snippet")
            if snippet and snippet != "—":
                parts.append("")
                parts.append(snippet)
            parts.append("")
            parts.append("Список: /jobs. Feedback: /jobs like <id>")
            await send_rich_markdown(
                bot,
                chat_id=chat_id,
                markdown="## Job hunt — скан готов\n\n" + "\n".join(parts),
            )

        ok, msg = start_background_job("job_scan", chat_id, _run_scan)
        await update.message.reply_text(
            f"{msg}\n\nПорог score ≥ {JOBHUNT_MIN_MATCH}. Результат придёт сюда."
        )
        return

    await reply_rich(update, _format_jobs_rich())


async def cmd_sources(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    from job_hunt.sources import format_sources_plain

    text = await asyncio.to_thread(format_sources_plain)
    await update.message.reply_text(text)


async def cmd_cover(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/cover <id> — короткий текст для HH/Habr\n"
            "/cover <id> email — письмо для email-отклика\n\n"
            "ID из `/jobs`"
        )
        return
    try:
        lead_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Неверный id. Пример: /cover 12")
        return

    channel = "hh"
    if len(context.args) > 1 and context.args[1].lower() in ("email", "mail", "e"):
        channel = "email"

    row = get_job_lead(lead_id)
    if not row:
        await update.message.reply_text(f"Лид #{lead_id} не найден. См. /jobs")
        return

    lead = _lead_row_to_dict(row)
    draft = await asyncio.to_thread(draft_cover_letter, lead, channel=channel)
    add_job_application(lead_id, cover_letter=draft["body"], status="draft")

    await reply_rich(update, format_draft_markdown(draft, lead_id=lead_id))


async def cmd_approve(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/approve source <key>\n"
            "/approve resume hh|habr|all\n\n"
            "Источники: /sources · diff резюме: /jobs sync"
        )
        return

    if context.args[0].lower() == "resume":
        await _approve_resume(update, context)
        return

    if context.args[0].lower() == "source":
        if len(context.args) < 2:
            await update.message.reply_text("Использование: /approve source <key>")
            return
        key = context.args[1].strip()
        from job_hunt.sources import approve_source

        ok = await asyncio.to_thread(approve_source, key)
        if ok:
            await update.message.reply_text(f"Источник {key} включён (active).")
        else:
            await update.message.reply_text(f"Источник {key} не найден. См. /sources")
        return

    if context.args[0].lower() == "bounty":
        await _approve_bounty(update, context)
        return

    await update.message.reply_text(
        "Неизвестная цель approve. Используй: source | resume"
    )


async def _approve_resume(update, context) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /approve resume hh|habr|linkedin|all\n\n"
            "Сначала: /jobs auth и /jobs sync"
        )
        return

    platform = context.args[1].lower()
    if platform not in ("hh", "habr", "linkedin", "all"):
        await update.message.reply_text("Платформа: hh, habr, linkedin, all")
        return

    result = await asyncio.to_thread(apply_sync, platform)
    lines = [f"## Resume sync — {platform}", ""]
    if not result.get("ok"):
        lines.append("**Статус:** частично или ошибка")
    else:
        lines.append("**Статус:** OK")

    for name, detail in (result.get("platforms") or {}).items():
        mark = "✅" if detail.get("ok") else "❌"
        lines.append(f"- {mark} **{name}:** {detail.get('message', '—')}")
        if detail.get("digest"):
            lines.append("")
            lines.append(detail["digest"])
            lines.append("")
        fields = detail.get("fields")
        if fields:
            lines.append(f"  _fields: {', '.join(fields)}_")

    await reply_rich(update, "\n".join(lines))


async def _approve_bounty(update, context) -> None:
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

    meta = get_bounty_draft_meta(draft_id)
    finding = BountyFinding.from_meta(meta)
    update_bounty_status(draft_id, "approved")

    lines = [
        f"## Отчёт #{draft_id} одобрен",
        "",
        f"**{draft['title']}**",
        "",
        draft["body"],
    ]

    if BOUNTY_AUTO_SUBMIT and finding:
        submit_result = await asyncio.to_thread(submit_finding, finding)
        if submit_result.ok:
            update_bounty_status(draft_id, "submitted")
            meta.update(
                {
                    "external_id": submit_result.external_id,
                    "report_url": submit_result.report_url,
                }
            )
            update_bounty_draft_meta(draft_id, meta)
            lines.extend(
                [
                    "",
                    f"**Сабмит:** {submit_result.message}",
                    f"**Ссылка:** {submit_result.report_url or '—'}",
                ]
            )
        elif submit_result.export_path:
            meta.update({"export_path": submit_result.export_path})
            update_bounty_draft_meta(draft_id, meta)
            lines.extend(
                [
                    "",
                    f"**Экспорт:** `{submit_result.export_path}`",
                    f"**Дальше:** {submit_result.message}",
                    f"**Программа:** {submit_result.report_url or finding.program_url}",
                    "_Статус «approved» — отправь вручную на платформе, затем: `python3 -m finance.bounty_payout --net-usd <net> --platform <platform> --report-id <id>`._",
                ]
            )
        else:
            update_bounty_status(draft_id, "submit_failed")
            lines.extend(
                [
                    "",
                    f"**Сабмит не удался:** {submit_result.message}",
                    "_Отчёт выше — можно отправить вручную на платформе программы._",
                ]
            )
    elif finding and finding.platform != "hackerone":
        lines.extend(
            [
                "",
                f"_Авто-сабмит для {finding.platform} пока недоступен._",
                f"Отправь вручную: {finding.program_url}",
            ]
        )
    elif not BOUNTY_AUTO_SUBMIT:
        lines.append("\n\n_Авто-сабмит выключен (BOUNTY_AUTO_SUBMIT=false)._")
    else:
        lines.append(
            "\n\n_Старый черновик без structured meta — отправь вручную по тексту выше._"
        )

    await reply_rich(update, "\n".join(lines))


async def cmd_reject_bounty(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/reject source <key>\n"
            "/reject bounty <id> (paused lane)"
        )
        return

    if context.args[0].lower() == "source":
        if len(context.args) < 2:
            await update.message.reply_text("Использование: /reject source <key>")
            return
        key = context.args[1].strip()
        from job_hunt.sources import reject_source

        ok = await asyncio.to_thread(reject_source, key)
        if ok:
            await update.message.reply_text(f"Источник {key} отклонён.")
        else:
            await update.message.reply_text(f"Источник {key} не найден.")
        return

    if context.args[0].lower() != "bounty":
        await update.message.reply_text("Использование: /reject source <key>")
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
    await reply_rich(update, f"## Черновик #{draft_id}\n\nОтклонён.")


async def cmd_finance(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await reply_rich(update, _format_finance_rich())


async def cmd_help(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await reply_rich(update, _help_text().replace("Команды бота:\n\n", "# Справка\n\n"))


async def post_init(app) -> None:
    from telegram import BotCommand

    commands = [BotCommand(cmd, desc) for cmd, desc in BOT_COMMANDS]
    await app.bot.set_my_commands(commands)
    try:
        await app.bot.set_my_description(
            "Career hunter: поиск сильных вакансий и проектов, feedback источников."
        )
        await app.bot.set_my_short_description(
            "Вакансии /jobs, источники /sources, задачи Cursor."
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
    from orchestrator.cursor_session import cleanup_stale_bridges_on_startup

    cleanup_stale_bridges_on_startup()

    from telegram.ext import Application, CommandHandler

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("status", cmd_status, block=False))
    app.add_handler(CommandHandler("finance", cmd_finance, block=False))
    app.add_handler(CommandHandler("task", cmd_task, block=False))
    app.add_handler(CommandHandler("ask", cmd_ask, block=False))
    app.add_handler(CommandHandler("pause", cmd_pause, block=False))
    app.add_handler(CommandHandler("resume", cmd_resume, block=False))
    app.add_handler(CommandHandler("memory", cmd_memory, block=False))
    app.add_handler(CommandHandler("bounty", cmd_bounty, block=False))
    app.add_handler(CommandHandler("jobs", cmd_jobs, block=False))
    app.add_handler(CommandHandler("sources", cmd_sources, block=False))
    app.add_handler(CommandHandler("cover", cmd_cover, block=False))
    app.add_handler(CommandHandler("approve", cmd_approve, block=False))
    app.add_handler(CommandHandler("reject", cmd_reject_bounty, block=False))
    app.add_handler(CommandHandler("help", cmd_help, block=False))
    app.add_handler(CommandHandler("start", cmd_help, block=False))

    logger.info("Telegram-бот запускается")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
