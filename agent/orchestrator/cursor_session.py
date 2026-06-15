"""Serialize Cursor SDK access — one local bridge at a time."""

from __future__ import annotations

import logging
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_holder: str | None = None
_since: str | None = None


class CursorBusyError(RuntimeError):
    """Raised when another task holds the Cursor SDK session."""

    def __init__(self, holder: str | None) -> None:
        self.holder = holder or "unknown"
        since = _since[:19] if _since else "?"
        super().__init__(
            f"Cursor агент занят ({self.holder}, с {since} UTC). "
            "Дождитесь завершения или проверьте /status."
        )


def cursor_holder() -> str | None:
    return _holder


def _reset_cursor_sdk_client() -> None:
    """Drop cached default Client/Bridge so the next call launches a fresh bridge."""
    try:
        from cursor_sdk._client import close_default_client

        close_default_client()
    except Exception:
        logger.debug("close_default_client skipped", exc_info=True)


@contextmanager
def cursor_session(owner: str, *, block: bool = True, timeout: float | None = None):
    """Exclusive Cursor SDK session."""
    global _holder, _since

    acquired = _lock.acquire(blocking=block, timeout=-1 if timeout is None else timeout)
    if not acquired:
        raise CursorBusyError(_holder)

    _holder = owner
    _since = datetime.now(timezone.utc).isoformat()
    _reset_cursor_sdk_client()
    try:
        yield
    finally:
        _holder = None
        _since = None
        _reset_cursor_sdk_client()
        time.sleep(0.3)
        _lock.release()


def cleanup_stale_bridges_on_startup() -> None:
    """Service boot: reset SDK singleton, then kill orphaned bridge PIDs."""
    _reset_cursor_sdk_client()
    from orchestrator.cursor_bridge import cleanup_cursor_bridge

    killed = cleanup_cursor_bridge(grace_sec=1.0)
    if killed:
        logger.info("Startup: cleaned %d orphan cursor-sdk-bridge process(es)", killed)
