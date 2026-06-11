"""Prepare agent markdown for Telegram Rich Messages (Bot API 10.1)."""

from __future__ import annotations

RICH_MAX = 32768
PLAIN_MAX = 4096

RICH_MARKDOWN_EXAMPLES: dict[str, str] = {
    "basic": """# Базовое форматирование

**жирный**, *курсив*, ~~зачёркнутый~~, `inline code`

==выделенный текст==, ||спойлер||

[ссылка на Telegram](https://t.me/)
""",
    "structure": """## Структура ответа

Параграф с **важным** словом и _акцентом_.

- пункт списка
- ещё пункт

1. нумерованный
2. второй пункт

> цитата
""",
    "code": """### Код

Inline: `pip install httpx`

```python
async def hello(name: str) -> str:
    return f"Привет, {name}!"
```
""",
    "table": """### Таблица

| Метрика | Значение |
|:--------|---------:|
| CPU     | **12%**  |
| RAM     | _48%_    |
""",
}


def get_rich_example(name: str) -> str | None:
    return RICH_MARKDOWN_EXAMPLES.get(name.strip().lower())


def list_rich_examples() -> list[str]:
    return sorted(RICH_MARKDOWN_EXAMPLES)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def stabilize_stream_markdown(text: str) -> str:
    body = text
    if body.count("```") % 2 == 1:
        body += "\n```"
    if body.count("~~~") % 2 == 1:
        body += "\n~~~"
    return body


def prepare_rich_markdown(text: str, *, streaming: bool = False) -> str:
    body = (text or "Пустой ответ.").strip()
    if streaming:
        body = stabilize_stream_markdown(body)
    return truncate(body, RICH_MAX)


def prepare_plain_markdown(text: str, *, streaming: bool = False) -> str:
    body = (text or "Пустой ответ.").strip()
    if streaming:
        body = stabilize_stream_markdown(body)
    return truncate(body, PLAIN_MAX)
