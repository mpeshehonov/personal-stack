"""Serialize Cursor SDK access — one local bridge at a time."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

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


@contextmanager
def cursor_session(owner: str, *, block: bool = True, timeout: float | None = None):
    """Exclusive Cursor SDK session.

    Do NOT kill bridge processes on exit — cursor-sdk shuts down its own bridge,
    and global cleanup races with the next session (Connection refused).
    """
    global _holder, _since

    acquired = _lock.acquire(blocking=block, timeout=-1 if timeout is None else timeout)
    if not acquired:
        raise CursorBusyError(_holder)

    _holder = owner
    _since = datetime.now(timezone.utc).isoformat()
    try:
        yield
    finally:
        _holder = None
        _since = None
        # Brief pause so the bridge port is released before the next waiter starts.
        time.sleep(0.3)
        _lock.release()


def cleanup_stale_bridges_on_startup() -> int:
    """Call once at bot/orchestrator start — not between requests."""
    from orchestrator.cursor_bridge import cleanup_cursor_bridge

    return cleanup_cursor_bridge(grace_sec=1.0)
