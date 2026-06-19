"""Job hunt autopilot — read-only vacancy scan and digest (Phase 0)."""

from job_hunt.scanner import daily_job_scan, scan_and_store_leads

__all__ = ["daily_job_scan", "scan_and_store_leads"]
