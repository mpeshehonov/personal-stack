"""Background jobs for Telegram bot — long tasks must not block other commands."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)


@dataclass
class BackgroundJob:
    name: str
    chat_id: int
    started_at: str
    task: asyncio.Task


_jobs: dict[str, BackgroundJob] = {}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def job_running(name: str) -> bool:
    job = _jobs.get(name)
    if not job:
        return False
    if job.task.done():
        _jobs.pop(name, None)
        return False
    return True


def list_running_jobs() -> list[str]:
    done = [k for k, j in _jobs.items() if j.task.done()]
    for k in done:
        _jobs.pop(k, None)
    return list(_jobs.keys())


def start_background_job(
    name: str,
    chat_id: int,
    coro_factory: Callable[[], Awaitable[None]],
) -> tuple[bool, str]:
    """Start named job if not already running."""
    if job_running(name):
        started = _jobs[name].started_at[:19]
        return False, f"Уже выполняется (с {started} UTC). /status — прогресс."

    async def _wrapper() -> None:
        try:
            await coro_factory()
        except asyncio.CancelledError:
            logger.info("Background job %s cancelled", name)
            raise
        except Exception:
            logger.exception("Background job %s failed", name)
        finally:
            _jobs.pop(name, None)

    task = asyncio.create_task(_wrapper(), name=f"bg:{name}")
    _jobs[name] = BackgroundJob(name=name, chat_id=chat_id, started_at=_utcnow(), task=task)
    return True, "Запущено в фоне."
