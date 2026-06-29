#!/usr/bin/env python3
"""CLI: check resume sync auth and show sync plan."""

from __future__ import annotations

import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1] / "agent"
sys.path.insert(0, str(AGENT_ROOT))

from job_hunt.resume_sync_cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
