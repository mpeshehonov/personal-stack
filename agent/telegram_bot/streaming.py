"""Telegram answer streaming: Rich Messages → Markdown → plain edit fallback."""

from __future__ import annotations

import logging
import time

from telegram import Bot
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest, TelegramError

from telegram_bot.rich_format import prepare_plain_markdown, prepare_rich_markdown
from telegram_bot.tg_rich_api import RichMessageApiError, send_rich_message, send_rich_message_draft

logger = logging.getLogger(__name__)

# Adaptive throttle: faster early stream, slower during long answers (~1 edit/sec limit).
THROTTLE_MIN_SEC = 0.35
THROTTLE_MAX_SEC = 0.95
THROTTLE_RAMP_START = 80
THROTTLE_RAMP_END = 450

MIN_PREVIEW = 8
MIN_DELTA_CHARS = 14
TYPING_INTERVAL_SEC = 4.0


class AnswerStreamer:
    def __init__(self, bot: Bot, chat_id: int, draft_id: int = 0) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.draft_id = draft_id or 1
        self._anchor_id: int | None = None
        self._last_sent = 0.0
        self._last_typing = 0.0
        self._last_text = ""
        self._last_raw_len = 0
        self._pending = ""
        self._mode = "rich"
        self._stream_visible = False

    async def start(self) -> None:
        msg = await self.bot.send_message(
            chat_id=self.chat_id,
            text="Обрабатываю запрос…",
        )
        self._anchor_id = msg.message_id
        self.draft_id = (self.chat_id * 997 + msg.message_id) % 2_000_000_000 or 1

    def _throttle_interval(self) -> float:
        n = len(self._pending)
        if n <= THROTTLE_RAMP_START:
            return THROTTLE_MIN_SEC
        if n >= THROTTLE_RAMP_END:
            return THROTTLE_MAX_SEC
        t = (n - THROTTLE_RAMP_START) / (THROTTLE_RAMP_END - THROTTLE_RAMP_START)
        return THROTTLE_MIN_SEC + t * (THROTTLE_MAX_SEC - THROTTLE_MIN_SEC)

    def _should_push(self, now: float, *, force: bool = False) -> bool:
        if not self._pending or self._pending == self._last_text:
            return False
        if not force and len(self._pending) < MIN_PREVIEW:
            return False
        if force:
            return True
        interval = self._throttle_interval()
        elapsed = now - self._last_sent
        delta = len(self._pending) - self._last_raw_len
        if elapsed >= interval * 1.75:
            return True
        return elapsed >= interval and delta >= MIN_DELTA_CHARS

    async def update(self, text: str) -> None:
        if not text or not text.strip():
            return
        self._pending = text.strip()
        now = time.monotonic()
        if not self._should_push(now):
            return
        await self._maybe_typing(now)
        await self._push(self._pending)
        self._last_sent = now

    async def finalize(self, text: str) -> None:
        body = (text or self._pending or "Пустой ответ.").strip()
        self._pending = body
        if self._should_push(time.monotonic(), force=True):
            await self._push(body)

        if self._mode == "rich":
            await self._finalize_rich(body)
        elif self._mode == "markdown":
            await self._finalize_markdown(body)
        else:
            await self._finalize_plain(body)

        await self._delete_anchor()

    async def _finalize_rich(self, text: str) -> None:
        markdown = prepare_rich_markdown(text)
        try:
            await send_rich_message(
                self.bot,
                chat_id=self.chat_id,
                markdown=markdown,
            )
            await self._clear_draft()
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
            await self._clear_draft()
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
        await self.bot.send_message(chat_id=self.chat_id, text=body)

    async def _push(self, text: str) -> None:
        if self._mode == "rich":
            await self._push_rich(text)
            return
        if self._mode == "markdown":
            await self._push_markdown(text)
            return
        await self._push_plain(text)

    async def _mark_stream_visible(self) -> None:
        if self._stream_visible:
            return
        self._stream_visible = True
        if self._mode in ("rich", "markdown"):
            await self._delete_anchor()

    async def _push_rich(self, text: str) -> None:
        markdown = prepare_rich_markdown(text, streaming=True)
        try:
            await send_rich_message_draft(
                self.bot,
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                markdown=markdown,
            )
            self._remember_push(text)
            await self._mark_stream_visible()
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
            self._remember_push(text)
            await self._mark_stream_visible()
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
            self._remember_push(text, rendered=preview)
            self._stream_visible = True
            return
        if preview == self._last_text:
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._anchor_id,
                text=preview,
            )
            self._remember_push(text, rendered=preview)
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("edit anchor: %s", e)

    def _remember_push(self, raw_text: str, *, rendered: str | None = None) -> None:
        self._last_text = rendered if rendered is not None else raw_text
        self._last_raw_len = len(raw_text)

    async def _maybe_typing(self, now: float) -> None:
        if now - self._last_typing < TYPING_INTERVAL_SEC:
            return
        self._last_typing = now
        try:
            await self.bot.send_chat_action(chat_id=self.chat_id, action=ChatAction.TYPING)
        except TelegramError:
            pass

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
