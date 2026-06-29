"""Habr Career session verification (push — Phase JH-14)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from job_hunt.config import HABR_PROFILE_SLUG, HABR_SESSION_COOKIE, JOBHUNT_USER_AGENT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HabrAuthStatus:
    ok: bool
    message: str
    profile_url: str = ""


def _cookie_header() -> str:
    raw = HABR_SESSION_COOKIE.strip()
    if not raw:
        return ""
    if "=" in raw and not raw.lower().startswith("cookie:"):
        return raw
    return raw


def verify_habr_auth() -> HabrAuthStatus:
    cookie = _cookie_header()
    if not cookie:
        return HabrAuthStatus(False, "HABR_SESSION_COOKIE не задан")

    slug = HABR_PROFILE_SLUG.strip() or "profile"
    url = f"https://career.habr.com/users/{slug}"
    try:
        resp = httpx.get(
            url,
            headers={
                "User-Agent": JOBHUNT_USER_AGENT,
                "Cookie": cookie,
                "Accept-Language": "ru-RU,ru;q=0.9",
            },
            timeout=30.0,
            follow_redirects=True,
        )
    except httpx.HTTPError as exc:
        return HabrAuthStatus(False, str(exc))

    if resp.status_code == 404:
        return HabrAuthStatus(False, f"Профиль не найден: {url}")
    if resp.status_code != 200:
        return HabrAuthStatus(False, f"HTTP {resp.status_code}")

    text = resp.text.lower()
    if "войти" in text and "регистрация" in text and "profile-settings" not in resp.url.path:
        return HabrAuthStatus(False, "Cookie недействителен (гостевая страница)")

    return HabrAuthStatus(True, "OK", profile_url=str(resp.url))


def sync_habr_profile(*, about_text: str, skills: list[str]) -> tuple[bool, str]:
    """Placeholder until JH-14 — verifies session only."""
    status = verify_habr_auth()
    if not status.ok:
        return False, status.message
    _ = (about_text, skills)
    return False, (
        "Habr push ещё не реализован (JH-14). Cookie OK — после approve агент обновит через API/Playwright."
    )
