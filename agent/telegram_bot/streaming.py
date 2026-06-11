"""Telegram answer streaming — one message bubble, typewriter reveal, Rich finalize."""

from __future__ import annotations

import asyncio
import logging
import time

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError

from telegram_bot.rich_format import prepare_plain_markdown, prepare_rich_markdown
from telegram_bot.tg_rich_api import RichMessageApiError, send_rich_message

logger = logging.getLogger(__name__)

# editMessageText ~1/sec; typewriter fills gaps between agent chunks.
EDIT_MIN_INTERVAL = 0.45
TYPEWRITER_TICK = 0.04
TYPEWRITER_CHARS_MIN = 2
TYPEWRITER_CHARS_MAX = 18
BACKLOG_FAST_THRESHOLD = 80


class AnswerStreamer:
    def __init__(self, bot: Bot, chat_id: int, draft_id: int = 0) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self._message_id: int | None = None
        self._target = ""
        self._shown_len = 0
        self._last_edit = 0.0
        self._last_rendered = ""
        self._typewriter: asyncio.Task | None = None
        self._closed = False

    async def start(self) -> None:
        msg = await self.bot.send_message(
            chat_id=self.chat_id,
            text="Обрабатываю запрос…",
        )
        self._message_id = msg.message_id

    async def update(self, text: str) -> None:
        if not text or not text.strip() or self._closed:
            return
        self._target = text.strip()
        self._ensure_typewriter()

    async def finalize(self, text: str) -> None:
        if self._closed:
            return
        self._target = (text or self._target or "Пустой ответ.").strip()
        await self._drain_typewriter()
        await self._finalize_rich(self._target)
        self._closed = True

    def _ensure_typewriter(self) -> None:
        if self._typewriter is None or self._typewriter.done():
            self._typewriter = asyncio.create_task(self._typewriter_loop())

    async def _drain_typewriter(self) -> None:
        self._ensure_typewriter()
        if self._typewriter:
            await self._typewriter
        while self._shown_len < len(self._target):
            self._shown_len = len(self._target)
            await self._render_partial(self._target)
            await asyncio.sleep(TYPEWRITER_TICK)

    async def _typewriter_loop(self) -> None:
        try:
            while not self._closed:
                if self._shown_len >= len(self._target):
                    await asyncio.sleep(TYPEWRITER_TICK)
                    continue
                backlog = len(self._target) - self._shown_len
                step = TYPEWRITER_CHARS_MIN
                if backlog > BACKLOG_FAST_THRESHOLD:
                    step = min(
                        TYPEWRITER_CHARS_MAX,
                        TYPEWRITER_CHARS_MIN + backlog // 25,
                    )
                elif backlog > 30:
                    step = min(TYPEWRITER_CHARS_MAX, TYPEWRITER_CHARS_MIN + backlog // 40)
                self._shown_len = min(len(self._target), self._shown_len + step)
                visible = self._target[: self._shown_len]
                await self._render_partial(visible)
                await asyncio.sleep(TYPEWRITER_TICK)
        except asyncio.CancelledError:
            pass

    async def _render_partial(self, visible: str) -> None:
        if self._message_id is None or not visible:
            return
        preview = prepare_plain_markdown(visible, streaming=True)
        if preview == self._last_rendered:
            return
        now = time.monotonic()
        if now - self._last_edit < EDIT_MIN_INTERVAL and len(preview) - len(self._last_rendered) < 24:
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._message_id,
                text=preview,
            )
            self._last_rendered = preview
            self._last_edit = now
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("stream edit: %s", e)
        except TelegramError as e:
            logger.warning("stream edit: %s", e)

    async def _finalize_rich(self, text: str) -> None:
        markdown = prepare_rich_markdown(text)
        try:
            await send_rich_message(
                self.bot,
                chat_id=self.chat_id,
                markdown=markdown,
            )
            if self._message_id is not None:
                try:
                    await self.bot.delete_message(
                        chat_id=self.chat_id,
                        message_id=self._message_id,
                    )
                except TelegramError:
                    pass
                self._message_id = None
            return
        except RichMessageApiError as e:
            logger.info("sendRichMessage unavailable: %s", e)
        await self._finalize_markdown(text)

    async def _finalize_markdown(self, text: str) -> None:
        body = prepare_plain_markdown(text)
        if self._message_id is None:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=body,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._message_id,
                text=body,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        except TelegramError as e:
            logger.warning("Markdown finalize edit: %s", e)
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._message_id,
                text=body,
            )
        except TelegramError as e:
            logger.warning("Plain finalize edit: %s", e)
            await self.bot.send_message(chat_id=self.chat_id, text=body)
