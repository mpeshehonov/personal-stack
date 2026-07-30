"""Opportunity OS — personal opportunity core (Jobs vertical first)."""

from opportunity.brief import format_opportunity_brief
from opportunity.feedback import apply_opportunity_feedback
from opportunity.migrate import migrate_opportunity_core
from opportunity.profile import format_profile_plain, load_profile, update_profile_fields
from opportunity.services import after_scan_hook, upsert_from_job_lead

__all__ = [
    "apply_opportunity_feedback",
    "after_scan_hook",
    "format_opportunity_brief",
    "format_profile_plain",
    "load_profile",
    "migrate_opportunity_core",
    "update_profile_fields",
    "upsert_from_job_lead",
]
