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

# Draft API supports faster updates; edits are ~1/sec per message.
DRAFT_THROTTLE_BASE = 0.28
DRAFT_THROTTLE_BURST = 0.14
EDIT_THROTTLE_SEC = 0.95
BURST_UPDATES = 4
MIN_PREVIEW = 5
MIN_DELTA_CHARS = 10


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
        self._push_count = 0
        self._draft_active = False

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
        if not self._should_push(self._pending, time.monotonic()):
            return
        await self._push(self._pending)
        self._last_sent = time.monotonic()

    async def finalize(self, text: str) -> None:
        body = (text or self._pending or "Пустой ответ.").strip()
        self._pending = body
        await self._flush_pending()

        if self._mode == "rich":
            await self._delete_anchor()
            await self._polish_draft_rich(body)
            await self._finalize_rich(body)
            await self._clear_draft()
            return
        if self._mode == "markdown":
            await self._delete_anchor()
            await self._polish_draft_markdown(body)
            await self._finalize_markdown(body)
            await self._clear_draft()
            return
        await self._finalize_plain(body)

    def _throttle_sec(self) -> float:
        if self._mode in ("rich", "markdown"):
            if self._push_count < BURST_UPDATES:
                return DRAFT_THROTTLE_BURST
            return DRAFT_THROTTLE_BASE
        return EDIT_THROTTLE_SEC

    def _should_push(self, text: str, now: float) -> bool:
        if text == self._last_text:
            return False
        if len(text) < MIN_PREVIEW and self._push_count > 0:
            return False
        elapsed = now - self._last_sent
        delta = len(text) - len(self._last_text)
        if elapsed >= self._throttle_sec():
            return True
        return delta >= MIN_DELTA_CHARS and elapsed >= DRAFT_THROTTLE_BURST

    async def _flush_pending(self) -> None:
        if self._pending and self._pending != self._last_text:
            await self._push(self._pending)
            self._last_sent = time.monotonic()

    async def _on_draft_started(self) -> None:
        if not self._draft_active:
            self._draft_active = True
            await self._delete_anchor()

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
        if self._anchor_id is not None:
            try:
                await self.bot.edit_message_text(
                    chat_id=self.chat_id,
                    message_id=self._anchor_id,
                    text=body,
                )
                self._anchor_id = None
                return
            except BadRequest as e:
                if "message is not modified" in str(e).lower():
                    self._anchor_id = None
                    return
                logger.warning("finalize plain edit: %s", e)
            except TelegramError as e:
                logger.warning("finalize plain edit: %s", e)
        await self.bot.send_message(chat_id=self.chat_id, text=body)

    async def _push(self, text: str) -> None:
        if self._mode == "rich":
            await self._push_rich(text)
            return
        if self._mode == "markdown":
            await self._push_markdown(text)
            return
        await self._push_plain(text)

    async def _polish_draft_rich(self, text: str) -> None:
        if not self._draft_active:
            return
        markdown = prepare_rich_markdown(text)
        try:
            await send_rich_message_draft(
                self.bot,
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                markdown=markdown,
            )
        except RichMessageApiError:
            pass

    async def _polish_draft_markdown(self, text: str) -> None:
        if not self._draft_active:
            return
        body = prepare_plain_markdown(text)
        try:
            await self.bot.send_message_draft(
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                text=body,
                parse_mode=ParseMode.MARKDOWN,
            )
        except (BadRequest, TelegramError):
            pass

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
            self._push_count += 1
            await self._on_draft_started()
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
            self._push_count += 1
            await self._on_draft_started()
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
            self._push_count += 1
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
            self._push_count += 1
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("edit anchor: %s", e)

    async def _clear_draft(self) -> None:
        if not self._draft_active:
            return
        try:
            await self.bot.send_message_draft(
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                text="",
            )
        except (BadRequest, TelegramError):
            pass
        self._draft_active = False

    async def _delete_anchor(self) -> None:
        if self._anchor_id is None:
            return
        try:
            await self.bot.delete_message(chat_id=self.chat_id, message_id=self._anchor_id)
        except TelegramError:
            pass
        self._anchor_id = None
