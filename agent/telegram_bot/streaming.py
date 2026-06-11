"""Telegram answer streaming: Rich Messages → Markdown → plain edit fallback."""

from __future__ import annotations

import logging
import time

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError

from telegram_bot.rich_format import prepare_plain_markdown, prepare_rich_markdown
from telegram_bot.tg_rich_api import RichMessageApiError, send_rich_message, send_rich_message_draft

logger = logging.getLogger(__name__)

THROTTLE_SEC = 0.55
MIN_PREVIEW = 20


class AnswerStreamer:
    def __init__(self, bot: Bot, chat_id: int, draft_id: int = 0) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.draft_id = draft_id or 1
        self._anchor_id: int | None = None
        self._last_sent = 0.0
        self._last_text = ""
        self._pending = ""
        self._mode = "rich"

    async def start(self) -> None:
        msg = await self.bot.send_message(
            chat_id=self.chat_id,
            text="Обрабатываю запрос…",
        )
        self._anchor_id = msg.message_id
        self.draft_id = (self.chat_id * 997 + msg.message_id) % 2_000_000_000 or 1

    async def update(self, text: str) -> None:
        if not text or not text.strip():
            return
        self._pending = text.strip()
        if len(self._pending) < MIN_PREVIEW:
            return
        now = time.monotonic()
        if self._pending == self._last_text or now - self._last_sent < THROTTLE_SEC:
            return
        await self._push(self._pending)
        self._last_sent = now

    async def finalize(self, text: str) -> None:
        body = (text or self._pending or "Пустой ответ.").strip()
        await self._clear_draft()
        await self._delete_anchor()
        if self._mode == "rich":
            await self._finalize_rich(body)
            return
        if self._mode == "markdown":
            await self._finalize_markdown(body)
            return
        await self._finalize_plain(body)

    async def _finalize_rich(self, text: str) -> None:
        markdown = prepare_rich_markdown(text)
        try:
            await send_rich_message(
                self.bot,
                chat_id=self.chat_id,
                markdown=markdown,
            )
            return
        except RichMessageApiError as e:
            logger.info("sendRichMessage unavailable: %s", e)
            self._mode = "markdown"
            await self._finalize_markdown(text)

    async def _finalize_markdown(self, text: str) -> None:
        body = prepare_plain_markdown(text)
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=body,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        except TelegramError as e:
            logger.warning("Markdown send failed: %s", e)
            await self._finalize_plain(text)

    async def _finalize_plain(self, text: str) -> None:
        body = prepare_plain_markdown(text)
        await self.bot.send_message(chat_id=self.chat_id, text=body)

    async def _push(self, text: str) -> None:
        if self._mode == "rich":
            await self._push_rich(text)
            return
        if self._mode == "markdown":
            await self._push_markdown(text)
            return
        await self._push_plain(text)

    async def _push_rich(self, text: str) -> None:
        markdown = prepare_rich_markdown(text, streaming=True)
        try:
            await send_rich_message_draft(
                self.bot,
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                markdown=markdown,
            )
            self._last_text = text
            return
        except RichMessageApiError as e:
            logger.info("sendRichMessageDraft unavailable: %s", e)
            self._mode = "markdown"
            await self._push_markdown(text)

    async def _push_markdown(self, text: str) -> None:
        preview = prepare_plain_markdown(text, streaming=True)
        try:
            await self.bot.send_message_draft(
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                text=preview,
                parse_mode=ParseMode.MARKDOWN,
            )
            self._last_text = text
            return
        except (BadRequest, TelegramError) as e:
            logger.info("message draft Markdown unavailable: %s", e)
            self._mode = "plain"
            await self._push_plain(text)

    async def _push_plain(self, text: str) -> None:
        preview = prepare_plain_markdown(text, streaming=True)
        if self._anchor_id is None:
            msg = await self.bot.send_message(chat_id=self.chat_id, text=preview)
            self._anchor_id = msg.message_id
            self._last_text = preview
            return
        if preview == self._last_text:
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._anchor_id,
                text=preview,
            )
            self._last_text = preview
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("edit anchor: %s", e)

    async def _clear_draft(self) -> None:
        try:
            await self.bot.send_message_draft(
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                text="",
            )
        except (BadRequest, TelegramError):
            pass

    async def _delete_anchor(self) -> None:
        if self._anchor_id is None:
            return
        try:
            await self.bot.delete_message(chat_id=self.chat_id, message_id=self._anchor_id)
        except TelegramError:
            pass
        self._anchor_id = None
