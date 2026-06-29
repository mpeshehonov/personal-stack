"""HH.ru applicant API — DEPRECATED 2025-12-15.

Applicant resume OAuth/API is closed. Use job_hunt.hh_digest for manual paste.
Browser automation: JH-16 (not implemented).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

HH_APPLICANT_API_CLOSED = "2025-12-15"
HH_DEPRECATED_MSG = (
    "API соискателя HH закрыт с 15.12.2025 — OAuth и PUT /resumes недоступны. "
    "См. /jobs hh-digest или docs/JOB-HUNT-AUTH-SETUP.md"
)


@dataclass(frozen=True)
class HhAuthStatus:
    ok: bool
    message: str
    resume_id: str = ""
    resume_title: str = ""


def verify_hh_auth() -> HhAuthStatus:
    return HhAuthStatus(False, HH_DEPRECATED_MSG)


def refresh_access_token() -> tuple[str, str]:
    return "", HH_DEPRECATED_MSG


def list_my_resumes(token: str) -> tuple[list, str]:
    _ = token
    return [], HH_DEPRECATED_MSG


def get_resume(token: str, resume_id: str) -> tuple[None, str]:
    _ = (token, resume_id)
    return None, HH_DEPRECATED_MSG


def build_hh_update_body(*, current: dict, title: str, description: str, skills: list[str]) -> dict:
    _ = (current, title, description, skills)
    return {}


def update_resume(token: str, resume_id: str, body: dict) -> tuple[bool, str]:
    _ = (token, resume_id, body)
    return False, HH_DEPRECATED_MSG


def publish_resume(token: str, resume_id: str) -> tuple[bool, str]:
    _ = (token, resume_id)
    return False, HH_DEPRECATED_MSG


def _effective_token() -> tuple[str, str]:
    return "", HH_DEPRECATED_MSG
