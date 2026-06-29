"""Job hunt autopilot — vacancy scan, resume sync, cover letters."""

from __future__ import annotations

from typing import Any

__all__ = ["daily_job_scan", "scan_and_store_leads"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from job_hunt.scanner import daily_job_scan, scan_and_store_leads

        return {"daily_job_scan": daily_job_scan, "scan_and_store_leads": scan_and_store_leads}[
            name
        ]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
