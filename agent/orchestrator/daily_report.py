"""Format daily cycle report for Telegram Rich Messages."""

from __future__ import annotations

import json
from typing import Any

from orchestrator.format_ru import run_status_ru
from orchestrator.health import HealthSnapshot, format_health


def format_finance_section(fin_summary: dict[str, Any]) -> str:
    """Human-readable multi-venue scan summary for daily Finance block."""
    if not fin_summary:
        return "—"

    lines: list[str] = []

    venues = fin_summary.get("venues") or []
    if venues:
        lines.append(f"**Venues:** {', '.join(venues)}")

    for h in fin_summary.get("venue_health") or []:
        ok = h.get("ok")
        status = "OK" if ok else "FAIL"
        detail = h.get("detail", "")
        lines.append(f"- `{h.get('venue', '?')}`: {status} — {detail}")

    by_venue = fin_summary.get("scan_by_venue") or {}
    if by_venue:
        parts = [f"{k}={v}" for k, v in sorted(by_venue.items())]
        total = fin_summary.get("markets_scanned", sum(by_venue.values()))
        lines.append(f"**Scanned:** {', '.join(parts)} ({total} total)")

    after = fin_summary.get("markets_after_filters")
    rejected = fin_summary.get("markets_rejected")
    if after is not None:
        lines.append(f"**After filters:** {after} tradeable, {rejected or 0} rejected")

    for sample in (fin_summary.get("rejection_samples") or [])[:2]:
        title = sample.get("title") or sample.get("market_title") or sample.get("id", "?")
        reasons = sample.get("reject_reasons") or []
        if len(title) > 40:
            title = title[:37] + "..."
        lines.append(f"  ↳ skip `{title}`: {'; '.join(reasons)}")

    proposals = fin_summary.get("proposals") or []
    lines.append(f"**Proposals:** {len(proposals)}")
    for p in proposals[:3]:
        venue = p.get("venue", "?")
        title = p.get("market_title") or "?"
        if len(title) > 44:
            title = title[:41] + "..."
        lines.append(f"  • [{venue}] {title} — {p.get('decision', '?')}")

    milestone = fin_summary.get("milestone") or {}
    goal = fin_summary.get("goal") or {}
    if milestone or goal:
        m_pct = milestone.get("progress_pct")
        g_pct = goal.get("progress_pct")
        parts = []
        if m_pct is not None:
            parts.append(f"M1 {m_pct:.0f}%")
        if g_pct is not None:
            parts.append(f"annual {g_pct:.0f}%")
        if parts:
            lines.append(f"**Goals:** {', '.join(parts)}")

    return "\n".join(lines) if lines else "—"


def format_daily_report_rich(
    *,
    health: HealthSnapshot,
    summary: str,
    fin_summary: dict[str, Any],
    draft_ids: list[int],
    commit_report: str,
    status: str = "finished",
) -> str:
    finance_block = format_finance_section(fin_summary)
    finance_json = json.dumps(fin_summary, indent=2, ensure_ascii=False)
    drafts = ", ".join(f"#{i}" for i in draft_ids) if draft_ids else "—"
    return f"""# Daily report

**Статус:** {run_status_ru(status)}

## Health

{format_health(health)}

## Agent

{summary.strip() or "—"}

## Finance

{finance_block}

<details>
<summary>Finance JSON</summary>

```json
{finance_json}
```

</details>

## Bug bounty

Черновики: {drafts}

## Git

{commit_report.strip() or "—"}
"""
