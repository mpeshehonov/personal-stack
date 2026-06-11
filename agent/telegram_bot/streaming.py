"""Progressive Telegram answer display via sendMessageDraft with edit fallback."""

from __future__ import annotations

import logging
import time

from telegram import Bot
from telegram.error import BadRequest, TelegramError

logger = logging.getLogger(__name__)

TG_MAX = 4096
THROTTLE_SEC = 0.4


class AnswerStreamer:
    """Stream assistant text to a private chat."""

    def __init__(self, bot: Bot, chat_id: int, draft_id: int) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.draft_id = draft_id
        self._last_sent = 0.0
        self._use_draft = True
        self._edit_message_id: int | None = None

    async def update(self, text: str) -> None:
        if not text.strip():
            return
        now = time.monotonic()
        if now - self._last_sent < THROTTLE_SEC:
            return
        await self._push(text)
        self._last_sent = now

    async def finalize(self, text: str) -> None:
        body = (text or "Пустой ответ.").strip()
        if len(body) > TG_MAX:
            body = body[: TG_MAX - 3] + "..."
        await self._clear_draft()
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=body)
        except TelegramError as e:
            logger.warning("finalize send_message failed: %s", e)
            if self._edit_message_id is not None:
                try:
                    await self.bot.edit_message_text(
                        chat_id=self.chat_id,
                        message_id=self._edit_message_id,
                        text=body,
                    )
                except TelegramError:
                    pass

    async def _clear_draft(self) -> None:
        if not self._use_draft:
            return
        try:
            await self.bot.send_message_draft(
                chat_id=self.chat_id,
                draft_id=self.draft_id,
                text="",
            )
        except (BadRequest, TelegramError):
            pass

    async def _push(self, text: str) -> None:
        preview = text if len(text) <= TG_MAX else text[: TG_MAX - 3] + "..."
        if self._use_draft:
            try:
                await self.bot.send_message_draft(
                    chat_id=self.chat_id,
                    draft_id=self.draft_id,
                    text=preview,
                )
                return
            except (BadRequest, TelegramError) as e:
                logger.info("send_message_draft unavailable, fallback to edit: %s", e)
                self._use_draft = False

        if self._edit_message_id is None:
            msg = await self.bot.send_message(chat_id=self.chat_id, text=preview)
            self._edit_message_id = msg.message_id
            return
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self._edit_message_id,
                text=preview,
            )
        except BadRequest as e:
            if "message is not modified" not in str(e).lower():
                logger.warning("edit_message_text failed: %s", e)
