"""Telegram bot — Russian UI, streaming /ask, task queue."""

from __future__ import annotations

import asyncio
import logging
import os
import re
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
from job_hunt.cover_service import (
    format_cover_body,
    format_cover_meta,
    looks_like_cover_request,
    produce_cover,
)
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
    ("start", "Меню и карточки вакансий"),
    ("menu", "Кнопки навигации"),
    ("help", "Справка"),
    ("brief", "Opportunity Brief на сегодня"),
    ("profile", "Профиль возможностей"),
    ("status", "Состояние сервера"),
    ("ask", "Вопрос агенту"),
    ("task", "Задача: правки + deploy"),
    ("jobs", "Карточки вакансий"),
    ("sources", "Источники"),
    ("cover", "Сопровод"),
    ("clients", "Карточки заказов FL/Kwork"),
    ("refresh", "Актуализация вакансий и заказов"),
    ("memory", "Итог daily"),
    ("pause", "Пауза автономии"),
    ("resume", "Снять паузу"),
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
        "/menu - кнопки внизу экрана\n"
        "/brief - Opportunity Brief (что делать сегодня)\n"
        "/clients - карточки заказов (как вакансии)\n"
        "/clients scan - поиск новых заказов\n"
        "/refresh - закрыть протухшие HH/FL/Kwork + обновить пути отклика\n"
        "/jobs - карточки вакансий (Ок / Мимо / Сопровод)\n"
        "/jobs scan - поиск новых вакансий\n"
        "/jobs dislike <id> paywall - мимо без штрафа источника\n"
        "/sources - веса источников\n"
        "/profile - профиль возможностей\n"
        "/cover <id|url|текст> [hh|tg|email] - сопровод\n"
        "/status /ask /task /memory\n"
        "/pause /resume\n\n"
        "Сопровод: «сопровод 42», ссылка HH/Hirify или вставь текст вакансии.\n"
        "Ещё: «откликнулся 76».\n"
        "Hirify: «Мимо» по умолчанию = paywall (источник не режем).\n"
        "Для плохого fit: /jobs dislike <id> bad_fit\n"
        "Уже откликнулся снаружи: жми «Откликнулся» или напиши «откликнулся 76».\n"
        "Тишина 3+ дня: /brief покажет follow-up.\n"
        "Income/bounty на паузе. Фокус: сильные действия."
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
    # Full message keeps newlines (needed for pasted JD + cover routing).
    raw_msg = (update.message.text or "").strip()
    text = re.sub(r"^/ask(@\w+)?\s*", "", raw_msg, count=1, flags=re.I).strip()
    if not text:
        await update.message.reply_text("Использование: /ask <вопрос>")
        return
    # Cover requests used to go through dumb /ask prompts — route to /cover pipeline
    if looks_like_cover_request(text):
        await _run_cover_pipeline(update, context, text)
        return
    await _run_streaming(update, context, text, mode="ask")


async def _run_cover_pipeline(update, context, raw: str) -> None:
    status = await update.message.reply_text("Пишу сопровод…")
    try:
        result = await asyncio.to_thread(produce_cover, raw, use_llm=True)
    except KeyError as exc:
        await status.edit_text(str(exc))
        return
    except ValueError as exc:
        await status.edit_text(str(exc))
        return
    except Exception as exc:
        logger.exception("cover pipeline failed")
        await status.edit_text(f"Не смог собрать сопровод: {exc}")
        return

    payload = result["payload"]
    draft = result["draft"]
    if payload.lead_id is not None:
        add_job_application(
            payload.lead_id,
            cover_letter=draft["body"],
            status="draft",
            notes=f"cover pipeline ({result.get('engine')})",
        )

    body = format_cover_body(result).strip()
    meta = format_cover_meta(result).strip()
    try:
        await status.delete()
    except Exception:
        pass
    # 1) ONLY the cover — plain text, easy copy. 2) meta separately if any.
    if not body:
        await update.message.reply_text("Пустой сопровод, попробуй ещё раз.")
        return
    await update.message.reply_text(body)
    if meta:
        await update.message.reply_text(meta)


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
            "/cover <id|url|текст> — сопровод",
            "/sources — веса источников",
        ]
    )
    return "\n".join(lines)


def _lead_row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


async def _send_job_cards(bot, chat_id: int, *, liked: bool = False) -> None:
    from telegram_bot.jobs_ui import (
        jobs_intro,
        lead_card_text,
        lead_keyboard,
        list_liked_leads,
        list_new_leads,
    )

    leads = list_liked_leads(10) if liked else list_new_leads(5)
    if not liked:
        await bot.send_message(chat_id=chat_id, text=jobs_intro(len(leads)))
    if not leads:
        if liked:
            await bot.send_message(chat_id=chat_id, text="Пока нет отмеченных «Ок».")
        return
    for row in leads:
        await bot.send_message(
            chat_id=chat_id,
            text=lead_card_text(row),
            reply_markup=lead_keyboard(int(row["id"]), row["url"] or ""),
            disable_web_page_preview=True,
        )


async def _start_job_scan(bot, chat_id: int, reply_func) -> None:
    if not JOBHUNT_ENABLED:
        await reply_func(
            "Job hunt отключён. Скопируй secrets/.env.jobhunt.template → secrets/.env.jobhunt"
        )
        return
    if job_running("job_scan"):
        await reply_func("Скан уже идёт. Подожди результат.")
        return

    async def _run_scan() -> None:
        summary = await asyncio.to_thread(scan_and_store_leads)
        by_source = summary.get("by_source") or {}
        source_line = ", ".join(
            f"{src} {count}" for src, count in by_source.items() if count
        ) or "-"
        parts = [
            f"Просмотрено: {summary.get('fetched', 0)} ({source_line})",
            f"Новых: {summary.get('new_count', 0)}",
            f"Ниже порога: {summary.get('below_threshold', 0)}, "
            f"в базе: {summary.get('skipped_existing', 0)}, "
            f"дубли: {summary.get('skipped_duplicates', 0)}",
        ]
        await send_rich_markdown(
            bot,
            chat_id=chat_id,
            markdown="## Скан готов\n\n" + "\n".join(parts),
        )
        await _send_job_cards(bot, chat_id)

    ok, msg = start_background_job("job_scan", chat_id, _run_scan)
    await reply_func(f"{msg}\nПорог score ≥ {JOBHUNT_MIN_MATCH}. Карточки придут сюда.")


async def _send_client_cards(bot, chat_id: int, *, liked: bool = False) -> None:
    from telegram_bot.jobs_ui import (
        client_card_text,
        client_keyboard,
        clients_intro,
        list_client_orders,
    )

    orders = list_client_orders(liked=liked, limit=5 if not liked else 10)
    if not liked:
        await bot.send_message(chat_id=chat_id, text=clients_intro(len(orders)))
    if not orders:
        if liked:
            await bot.send_message(chat_id=chat_id, text="Нет заказов в избранном.")
        return
    if liked:
        await bot.send_message(chat_id=chat_id, text=f"Заказы в избранном: {len(orders)}")
    for opp in orders:
        await bot.send_message(
            chat_id=chat_id,
            text=client_card_text(opp),
            reply_markup=client_keyboard(int(opp.id), opp.source_url or ""),
            disable_web_page_preview=True,
        )


async def _start_client_scan(bot, chat_id: int, reply_func) -> None:
    if job_running("client_scan"):
        await reply_func("Скан заказов уже идёт. Подожди.")
        return

    async def _run() -> None:
        from opportunity.client_scan import ensure_client_orders

        scan = await asyncio.to_thread(ensure_client_orders)
        parts = [
            f"Живых нашли: {scan.get('kept', 0)}",
            f"В базу: {scan.get('upserted', 0)}",
            f"Снесено закрытых/мёртвых: {scan.get('purged_dead', 0)}",
            f"Источники: {', '.join(scan.get('sources') or []) or '—'}",
        ]
        await send_rich_markdown(
            bot,
            chat_id=chat_id,
            markdown="## Скан заказов\n\n" + "\n".join(parts),
        )
        await _send_client_cards(bot, chat_id)

    ok, msg = start_background_job("client_scan", chat_id, _run)
    await reply_func(f"{msg}\nИщу свежие FL.ru / Kwork / TG (без Хабр Фриланса).")


async def _start_refresh_open(bot, chat_id: int, reply_func) -> None:
    if job_running("refresh_open"):
        await reply_func("Актуализация уже идёт.")
        return

    async def _run() -> None:
        from opportunity.refresh_open import refresh_open_pipeline

        result = await asyncio.to_thread(refresh_open_pipeline, rescan=True)
        clients = result.get("clients") or {}
        jobs = result.get("jobs") or {}
        cscan = result.get("client_scan") or {}
        jscan = result.get("job_scan") or {}
        parts = [
            f"Снято закрытых: {result.get('archived_total', 0)}",
            f"Перепроверка заказов: {clients.get('checked', 0)} "
            f"(архив {clients.get('archived', 0)})",
            f"Перепроверка вакансий: {jobs.get('checked', 0)} "
            f"(архив {jobs.get('archived', 0)})",
            f"Новый скан заказов: в базу {cscan.get('upserted', 0)} "
            f"(живых {cscan.get('kept', 0)})",
            f"Новый скан вакансий: новых {jscan.get('new_count', 0)} "
            f"(просмотрено {jscan.get('fetched', 0)})",
            f"Research-ссылки: {result.get('research_updated', 0)}",
        ]
        c_reasons = clients.get("reasons") or {}
        if c_reasons:
            parts.append(f"Почему сняли: {c_reasons}")
        await send_rich_markdown(
            bot,
            chat_id=chat_id,
            markdown="## Актуализация\n\n" + "\n".join(parts),
        )
        await _send_job_cards(bot, chat_id)
        await _send_client_cards(bot, chat_id)

    ok, msg = start_background_job("refresh_open", chat_id, _run)
    await reply_func(
        f"{msg}\nЗакрытые выкидываю + новый скан вакансий/заказов, потом пришлю карточки."
    )


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
            await update.message.reply_text(
                "Проще нажать Ок / Мимо на карточке. Или: /jobs like 12"
            )
            return
        try:
            lead_id = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Неверный id. Лучше кнопки на карточке.")
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
            f"{action} #{result['lead_id']}: {result['company']} - {result['title'][:60]}",
            f"Источник {result['source_key']}: {result['weight_before']} -> {result['weight_after']}",
        ]
        if result.get("source_weight_skipped"):
            lines.append("Вес источника не трогали (paywall/actionability).")
        if result.get("disabled"):
            lines.append("Источник отключён из-за низкого веса.")
        if result.get("next_action"):
            lines.append(f"Next: {result['next_action']}")
        await update.message.reply_text("\n".join(lines))
        return

    if context.args and context.args[0].lower() == "scan":
        await _start_job_scan(
            context.bot,
            update.effective_chat.id,
            update.message.reply_text,
        )
        return

    await _send_job_cards(context.bot, update.effective_chat.id)


async def cmd_sources(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    from job_hunt.sources import format_sources_plain
    from telegram_bot.jobs_ui import sources_keyboard

    text = await asyncio.to_thread(format_sources_plain)
    await update.message.reply_text(text, reply_markup=sources_keyboard())


async def cmd_menu(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    from telegram_bot.jobs_ui import MENU_KEYBOARD

    await update.message.reply_text(
        "Меню внизу: Вакансии / Заказы · Скан · Обновить (актуализация ссылок).",
        reply_markup=MENU_KEYBOARD,
    )


async def on_menu_text(update, context) -> None:
    if not update.message or not update.message.text:
        return
    if not _allowed_user(update.effective_user):
        return
    from telegram_bot.jobs_ui import parse_menu_text

    action = parse_menu_text(update.message.text)
    if not action:
        await _try_job_free_text(update, context)
        return
    if action == "jobs":
        await _send_job_cards(context.bot, update.effective_chat.id)
    elif action == "clients":
        await _send_client_cards(context.bot, update.effective_chat.id)
    elif action == "brief":
        await cmd_brief(update, context)
    elif action == "liked":
        await _send_job_cards(context.bot, update.effective_chat.id, liked=True)
        await _send_client_cards(context.bot, update.effective_chat.id, liked=True)
    elif action == "scan":
        await _start_job_scan(
            context.bot, update.effective_chat.id, update.message.reply_text
        )
    elif action == "client_scan":
        await _start_client_scan(
            context.bot, update.effective_chat.id, update.message.reply_text
        )
    elif action == "refresh":
        await _start_refresh_open(
            context.bot, update.effective_chat.id, update.message.reply_text
        )
    elif action == "sources":
        await cmd_sources(update, context)
    elif action == "help":
        await cmd_help(update, context)
    elif action == "menu":
        await cmd_menu(update, context)


async def _try_job_free_text(update, context) -> bool:
    """Route «сопровод #42» / URL / pasted JD / «откликнулся 76»."""
    import re

    text = (update.message.text or "").strip()
    low = text.lower()
    ids = [int(x) for x in re.findall(r"#?(\d{1,5})", text)]

    if looks_like_cover_request(text) or (
        any(k in low for k in ("сопровод", "cover", "сопроводительн")) and ids
    ):
        await _run_cover_pipeline(update, context, text)
        return True

    if any(k in low for k in ("откликнул", "откликн", "applied")) and ids:
        from job_hunt.sources import apply_feedback

        lead_id = ids[0]
        try:
            result = await asyncio.to_thread(
                apply_feedback, lead_id, "applied", note="free-text mark"
            )
        except KeyError:
            await update.message.reply_text(f"Лид #{lead_id} не найден.")
            return True
        await update.message.reply_text(
            f"Отклик зафиксирован #{result['lead_id']}: {result['company']}\n"
            f"{result['title'][:80]}"
        )
        return True

    return False


async def on_job_callback(update, context) -> None:
    query = update.callback_query
    if not query or not _allowed_user(query.from_user):
        return
    await query.answer()
    from telegram_bot.jobs_ui import parse_job_callback

    action, lead_id = parse_job_callback(query.data or "")
    chat_id = query.message.chat_id if query.message else query.from_user.id

    if action == "more":
        await _send_job_cards(context.bot, chat_id)
        return
    if action == "scan":
        await _start_job_scan(context.bot, chat_id, query.message.reply_text)
        return
    if lead_id is None:
        return

    if action == "like":
        from job_hunt.sources import apply_feedback

        try:
            result = await asyncio.to_thread(apply_feedback, lead_id, "like")
        except KeyError:
            await query.edit_message_text(f"Лид #{lead_id} не найден.")
            return
        await query.edit_message_text(
            f"В избранное #{result['lead_id']}: {result['company']}\n"
            f"{result['title'][:80]}\n"
            "Дальше: открой вакансию → откликнись → «Откликнулся»."
        )
        return

    if action == "applied":
        from job_hunt.sources import apply_feedback

        try:
            result = await asyncio.to_thread(apply_feedback, lead_id, "applied")
        except KeyError:
            await query.edit_message_text(f"Лид #{lead_id} не найден.")
            return
        await query.edit_message_text(
            f"Отклик зафиксирован #{result['lead_id']}: {result['company']}\n"
            f"{result['title'][:80]}\n"
            "Если 3+ дня тишина — в следующем /brief будет follow-up."
        )
        return

    if action == "pass":
        from job_hunt.sources import apply_feedback

        try:
            result = await asyncio.to_thread(apply_feedback, lead_id, "dislike")
        except KeyError:
            await query.edit_message_text(f"Лид #{lead_id} не найден.")
            return
        extra = ""
        if result.get("source_weight_skipped"):
            extra = "\nВес источника сохранён (paywall/Hirify)."
        elif result.get("disabled"):
            extra = "\nИсточник отключён."
        await query.edit_message_text(
            f"Мимо #{result['lead_id']}: {result['company']}\n"
            f"{result['title'][:80]}\n"
            f"Источник {result['source_key']}: {result['weight_before']} -> {result['weight_after']}"
            f"{extra}"
        )
        return

    if action == "cover":
        lead = get_job_lead(lead_id)
        if not lead:
            await query.message.reply_text(f"Лид #{lead_id} не найден.")
            return
        await query.message.reply_text(f"Пишу сопровод #{lead_id}…")
        src = str(lead["source"] or "")
        cover_channel = "tg" if src.startswith("tg:") or src == "telegram" else "hh"
        try:
            result = await asyncio.to_thread(
                produce_cover, f"/cover {lead_id} {cover_channel}", use_llm=True
            )
            draft = result["draft"]
            add_job_application(
                lead_id,
                cover_letter=draft["body"],
                status="draft",
                notes=f"telegram button ({result.get('engine')})",
            )
            # Keep in shortlist until user marks applied
            if (lead["status"] or "new") == "new":
                from job_hunt.sources import apply_feedback

                await asyncio.to_thread(apply_feedback, lead_id, "like", note="cover drafted")
        except Exception as exc:
            logger.exception("cover draft failed for %s", lead_id)
            await query.message.reply_text(f"Не смог собрать сопровод #{lead_id}: {exc}")
            return
        body = format_cover_body(result).strip()
        meta = format_cover_meta(result).strip()
        if body:
            await context.bot.send_message(chat_id=chat_id, text=body)
        if meta:
            await context.bot.send_message(chat_id=chat_id, text=meta)
        return


async def cmd_clients(update, context) -> None:
    """CLIENT order cards — same navigation pattern as /jobs."""
    if not _allowed_user(update.effective_user):
        return
    args = [a.lower() for a in (context.args or [])]
    if args and args[0] in ("scan", "hunt", "search"):
        await _start_client_scan(
            context.bot, update.effective_chat.id, update.message.reply_text
        )
        return
    if args and args[0] in ("liked", "ok", "saved"):
        await _send_client_cards(context.bot, update.effective_chat.id, liked=True)
        return
    if args and args[0] in ("refresh", "actualize", "purge"):
        await _start_refresh_open(
            context.bot, update.effective_chat.id, update.message.reply_text
        )
        return
    await _send_client_cards(context.bot, update.effective_chat.id)


async def cmd_refresh(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    await _start_refresh_open(
        context.bot, update.effective_chat.id, update.message.reply_text
    )


async def cmd_brief(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    from opportunity.brief import build_opportunity_brief
    from opportunity.migrate import ensure_migrated_on_startup
    from telegram_bot.jobs_ui import brief_lead_keyboard, brief_nav_keyboard

    def _build() -> dict:
        ensure_migrated_on_startup()
        return build_opportunity_brief()

    data = await asyncio.to_thread(_build)
    header = data["header"]
    if len(header) > 4000:
        header = header[:3990] + "\n…"
    await update.message.reply_text(header, reply_markup=brief_nav_keyboard())

    for card in data.get("cards") or []:
        lead_id = card.get("lead_id")
        text = card.get("text") or ""
        if len(text) > 3500:
            text = text[:3490] + "\n…"
        if not lead_id:
            await update.message.reply_text(text)
            continue
        await update.message.reply_text(
            text,
            reply_markup=brief_lead_keyboard(
                int(lead_id),
                card.get("url") or "",
                buttons=card.get("buttons") or {},
            ),
            disable_web_page_preview=True,
        )

    from telegram_bot.jobs_ui import brief_vertical_keyboard

    for card in data.get("vertical_cards") or []:
        text = card.get("text") or ""
        if len(text) > 3500:
            text = text[:3490] + "\n…"
        oid = card.get("opportunity_id")
        if not oid:
            await update.message.reply_text(text)
            continue
        await update.message.reply_text(
            text,
            reply_markup=brief_vertical_keyboard(int(oid), card.get("url") or ""),
            disable_web_page_preview=True,
        )

    if data.get("followup_text"):
        fu = data["followup_text"]
        if len(fu) > 4000:
            fu = fu[:3990] + "\n…"
        await update.message.reply_text(fu, disable_web_page_preview=True)

    if data.get("digest"):
        digest = data["digest"]
        if len(digest) > 4000:
            digest = digest[:3990] + "\n…"
        await update.message.reply_text(digest)


async def on_opp_callback(update, context) -> None:
    query = update.callback_query
    if not query or not _allowed_user(query.from_user):
        return
    await query.answer()
    from telegram_bot.jobs_ui import parse_opp_callback
    from opportunity.feedback import apply_opportunity_feedback

    action, opp_id = parse_opp_callback(query.data or "")
    chat_id = query.message.chat_id if query.message else query.from_user.id
    reply = query.message.reply_text if query.message else context.bot.send_message

    if action == "more":
        await _send_client_cards(context.bot, chat_id)
        return
    if action == "scan":
        await _start_client_scan(context.bot, chat_id, reply)
        return
    if action == "refresh":
        await _start_refresh_open(context.bot, chat_id, reply)
        return
    if action == "liked":
        await _send_client_cards(context.bot, chat_id, liked=True)
        return
    if opp_id is None:
        return
    mapping = {
        "like": "LIKE",
        "pass": "DISLIKE",
        "done": "APPLY",
    }
    fb = mapping.get(action)
    if not fb:
        return
    try:
        result = await asyncio.to_thread(
            apply_opportunity_feedback,
            opportunity_id=opp_id,
            action=fb,
            reason="" if action != "pass" else "skip vertical",
        )
    except KeyError:
        await query.edit_message_text(f"Opportunity #{opp_id} не найден.")
        return
    label = {"like": "Ок", "pass": "Мимо", "done": "Откликнулся"}.get(action, action)
    await query.edit_message_text(
        f"{label} заказ #{result.get('opportunity_id')}: {result.get('company') or '—'}\n"
        f"{(result.get('title') or '')[:100]}"
    )


async def cmd_profile(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    from opportunity.profile import format_profile_plain, update_profile_fields

    if context.args and context.args[0].lower() == "set" and len(context.args) >= 2:
        # /profile set remote_preference=remote_only
        assignments = " ".join(context.args[1:])
        fields: dict = {}
        for part in assignments.split():
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            if v.startswith("[") or v.startswith("{"):
                continue
            if v.isdigit():
                fields[k] = int(v)
            else:
                fields[k] = v
        if not fields:
            await update.message.reply_text(
                "Пример: /profile set remote_preference=remote_only"
            )
            return
        await asyncio.to_thread(update_profile_fields, **fields)
        await update.message.reply_text("Обновлено:\n" + "\n".join(f"{k}={v}" for k, v in fields.items()))
        return

    text = await asyncio.to_thread(format_profile_plain)
    await update.message.reply_text(text)


async def cmd_cover(update, context) -> None:
    if not _allowed_user(update.effective_user):
        return
    # Full message text (keeps newlines). args-join used to smash JD into one line.
    raw = (update.message.text or "").strip()
    if not raw or raw.lower().strip() in ("/cover", "/cover@"):
        await update.message.reply_text(
            "Использование:\n"
            "/cover tg\n"
            "<вставь текст вакансии>\n\n"
            "/cover hh https://hh.ru/vacancy/…\n"
            "/cover 42 tg\n"
            "/cover email <текст или ссылка>\n\n"
            "Ответ: 1) только сопровод 2) meta отдельным сообщением."
        )
        return
    await _run_cover_pipeline(update, context, raw)


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

    from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

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
    app.add_handler(CommandHandler("brief", cmd_brief, block=False))
    app.add_handler(CommandHandler("clients", cmd_clients, block=False))
    app.add_handler(CommandHandler("refresh", cmd_refresh, block=False))
    app.add_handler(CommandHandler("profile", cmd_profile, block=False))
    app.add_handler(CommandHandler("sources", cmd_sources, block=False))
    app.add_handler(CommandHandler("menu", cmd_menu, block=False))
    app.add_handler(CommandHandler("cover", cmd_cover, block=False))
    app.add_handler(CommandHandler("approve", cmd_approve, block=False))
    app.add_handler(CommandHandler("reject", cmd_reject_bounty, block=False))
    app.add_handler(CommandHandler("help", cmd_help, block=False))
    app.add_handler(CommandHandler("start", cmd_menu, block=False))
    app.add_handler(CallbackQueryHandler(on_job_callback, pattern=r"^j:", block=False))
    app.add_handler(CallbackQueryHandler(on_opp_callback, pattern=r"^o:", block=False))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_menu_text, block=False)
    )

    logger.info("Telegram-бот запускается")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
