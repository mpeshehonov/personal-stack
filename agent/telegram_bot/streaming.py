"""Telegram answer streaming via editMessageText (stable in private chats)."""

from __future__ import annotations

import logging
import time

from telegram import Bot
from telegram.error import BadRequest, TelegramError

logger = logging.getLogger(__name__)

TG_MAX = 4096
THROTTLE_SEC = 0.55
MIN_PREVIEW = 24


class AnswerStreamer:
    """Stream text by editing one anchor message."""

    def __init__(self, bot: Bot, chat_id: int, draft_id: int = 0) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self._message_id: int | None = None
        self._last_sent = 0.0
        self._last_text = ""
        self._pending = ""

    async def start(self) -> None:
        msg = await self.bot.send_message(
            chat_id=self.chat_id,
            text="Обрабатываю запрос…",
        )
        self._message_id = msg.message_id

    async def update(self, text: str) -> None:
        if not text or not text.strip():
            return
        self._pending = text.strip()
        if len(self._pending) < MIN_PREVIEW:
            return
        now = time.monotonic()
        if (
            self._pending != self._last_text
            and now - self._last_sent >= THROTTLE_SEC
        ):
            await self._edit(self._pending)
            self._last_sent = now

    async def finalize(self, text: str) -> None:
        body = (text or self._pending or "Пустой ответ.").strip()
        if self._message_id is None:
            await self.bot.send_message(chat_id=self.chat_id, text=body[:TG_MAX])
            return

        if len(body) <= TG_MAX:
            await self._edit(body)
            return

        await self._edit(body[: TG_MAX - 20] + "\n\n(продолжение ниже)")
        rest = body[TG_MAX - 20 :]
        while rest:
            chunk = rest[:TG_MAX]
            rest = rest[TG_MAX:]
            await self.bot.send_message(chat_id=self.chat_id, text=chunk)

    async def _edit(self, text: str) -> None:
        if self._message_id is None:
            return
        preview = text if len(text) <= TG_MAX else text[: TG_MAX - 3] + "…"
        if preview == self._last_text:
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._message_id,
                text=preview,
            )
            self._last_text = preview
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("edit_message_text: %s", e)
        except TelegramError as e:
            logger.warning("edit_message_text failed: %s", e)
