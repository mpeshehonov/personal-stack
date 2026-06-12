"""Format daily cycle report for Telegram Rich Messages."""

from __future__ import annotations

import json
from typing import Any

from orchestrator.format_ru import run_status_ru
from orchestrator.health import HealthSnapshot, format_health


def format_daily_report_rich(
    *,
    health: HealthSnapshot,
    summary: str,
    fin_summary: dict[str, Any],
    draft_ids: list[int],
    commit_report: str,
    status: str = "finished",
) -> str:
    finance_block = json.dumps(fin_summary, indent=2, ensure_ascii=False)
    drafts = ", ".join(f"#{i}" for i in draft_ids) if draft_ids else "—"
    return f"""# Daily report

**Статус:** {run_status_ru(status)}

## Health

{format_health(health)}

## Agent

{summary.strip() or "—"}

## Finance

```json
{finance_block}
```

## Bug bounty

Черновики: {drafts}

## Git

{commit_report.strip() or "—"}
"""
