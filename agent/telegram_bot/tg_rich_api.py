"""Raw Bot API 10.1 calls for Rich Messages."""

from __future__ import annotations

import httpx
from telegram import Bot


class RichMessageApiError(Exception):
    def __init__(self, description: str, payload: dict | None = None) -> None:
        super().__init__(description)
        self.description = description
        self.payload = payload or {}


async def _post(bot: Bot, method: str, payload: dict) -> dict:
    url = f"{bot.base_url}/{method}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        data = response.json()
    if not data.get("ok"):
        raise RichMessageApiError(data.get("description", "Unknown Telegram API error"), data)
    return data


async def send_rich_message_draft(
    bot: Bot,
    *,
    chat_id: int,
    draft_id: int,
    markdown: str,
) -> bool:
    data = await _post(
        bot,
        "sendRichMessageDraft",
        {
            "chat_id": chat_id,
            "draft_id": draft_id,
            "rich_message": {"markdown": markdown},
        },
    )
    return bool(data.get("result"))


async def send_rich_message(
    bot: Bot,
    *,
    chat_id: int,
    markdown: str,
) -> dict:
    return await _post(
        bot,
        "sendRichMessage",
        {
            "chat_id": chat_id,
            "rich_message": {"markdown": markdown},
        },
    )
