"""Cleanup orphaned Cursor SDK local bridge processes on the server."""

from __future__ import annotations

import logging
import subprocess
import time

from orchestrator.config import STACK_DIR

logger = logging.getLogger(__name__)

_BRIDGE_MARKER = "cursor-sdk-bridge"
_WORKSPACE = str(STACK_DIR)


def list_cursor_bridge_pids() -> list[int]:
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,args"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    pids: list[int] = []
    for line in result.stdout.splitlines():
        if _BRIDGE_MARKER not in line or _WORKSPACE not in line:
            continue
        parts = line.strip().split(None, 1)
        if not parts:
            continue
        try:
            pids.append(int(parts[0]))
        except ValueError:
            continue
    return pids


def cleanup_cursor_bridge(*, grace_sec: float = 2.0) -> int:
    """Terminate stale bridge processes for this workspace. Returns kill count."""
    pids = list_cursor_bridge_pids()
    if not pids:
        return 0

    for pid in pids:
        try:
            subprocess.run(["kill", str(pid)], timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass

    if grace_sec > 0:
        time.sleep(grace_sec)

    remaining = list_cursor_bridge_pids()
    for pid in remaining:
        try:
            subprocess.run(["kill", "-9", str(pid)], timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass

    killed = len(pids)
    if killed:
        logger.info("Cleaned up %d cursor-sdk-bridge process(es)", killed)
    return killed
