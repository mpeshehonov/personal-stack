"""LinkedIn session check — full profile write not available via public API."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from job_hunt.config import JOBHUNT_USER_AGENT, LINKEDIN_JSESSIONID, LINKEDIN_LI_AT


@dataclass(frozen=True)
class LinkedInAuthStatus:
    ok: bool
    message: str


def verify_linkedin_auth() -> LinkedInAuthStatus:
    li_at = LINKEDIN_LI_AT.strip()
    if not li_at:
        return LinkedInAuthStatus(False, "LINKEDIN_LI_AT не задан (опционально)")

    cookie_parts = [f"li_at={li_at}"]
    if LINKEDIN_JSESSIONID.strip():
        cookie_parts.append(f"JSESSIONID={LINKEDIN_JSESSIONID.strip()}")

    try:
        resp = httpx.get(
            "https://www.linkedin.com/voyager/api/me",
            headers={
                "User-Agent": JOBHUNT_USER_AGENT,
                "Cookie": "; ".join(cookie_parts),
                "Accept": "application/vnd.linkedin.normalized+json+2.1",
            },
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        return LinkedInAuthStatus(False, str(exc))

    if resp.status_code == 401:
        return LinkedInAuthStatus(False, "401 — li_at просрочен, экспортируй cookie заново")
    if resp.status_code != 200:
        return LinkedInAuthStatus(False, f"HTTP {resp.status_code}")

    return LinkedInAuthStatus(True, "OK — auto-write недоступен; агент напомнит про PDF с сайта")


def linkedin_sync_note(*, pdf_url: str) -> str:
    return f"LinkedIn: обнови профиль вручную или загрузи PDF: {pdf_url}"
