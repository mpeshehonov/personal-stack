"""Send Rich Messages from bot handlers and orchestrator notifications."""

from __future__ import annotations

import logging
import os

import httpx
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from orchestrator.config import load_env_file
from telegram_bot.rich_format import prepare_plain_markdown, prepare_rich_markdown
from telegram_bot.tg_rich_api import RichMessageApiError, send_rich_message

logger = logging.getLogger(__name__)


async def send_rich_markdown(bot: Bot, *, chat_id: int, markdown: str) -> None:
    body = prepare_rich_markdown(markdown)
    try:
        await send_rich_message(bot, chat_id=chat_id, markdown=body)
        return
    except RichMessageApiError as e:
        logger.info("sendRichMessage failed, fallback: %s", e.description)
    plain = prepare_plain_markdown(markdown)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=plain,
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramError:
        await bot.send_message(chat_id=chat_id, text=plain)


async def reply_rich(update, markdown: str) -> None:
    if not update.message:
        return
    await send_rich_markdown(
        update.get_bot(),
        chat_id=update.effective_chat.id,
        markdown=markdown,
    )


async def _post_telegram_api(token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        return response.json()


async def notify_allowed_users(markdown: str) -> None:
    """Push Rich Message to TELEGRAM_ALLOWED_USER_IDS (orchestrator daily, etc.)."""
    load_env_file(".env.telegram")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_ids = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "")
    if not token or not chat_ids:
        logger.info("Telegram notify skipped (no token or chat ids): %s", markdown[:120])
        return

    body = prepare_rich_markdown(markdown)
    for uid in chat_ids.split(","):
        uid = uid.strip()
        if not uid:
            continue
        try:
            data = await _post_telegram_api(
                token,
                "sendRichMessage",
                {
                    "chat_id": int(uid),
                    "rich_message": {"markdown": body},
                },
            )
            if data.get("ok"):
                continue
            logger.info("sendRichMessage failed for %s: %s", uid, data.get("description"))
            plain = prepare_plain_markdown(markdown)
            await _post_telegram_api(
                token,
                "sendMessage",
                {
                    "chat_id": int(uid),
                    "text": plain[:4096],
                    "parse_mode": "Markdown",
                },
            )
        except Exception as e:
            logger.warning("Telegram notify failed for %s: %s", uid, e)
