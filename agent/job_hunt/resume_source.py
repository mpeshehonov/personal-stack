"""Canonical resume payload from site source (resume.json + resume.md)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orchestrator.config import SITE_DIR

RESUME_JSON = SITE_DIR / "content" / "resume" / "resume.json"
RESUME_MD = SITE_DIR / "content" / "resume" / "resume.md"


@dataclass(frozen=True)
class ResumePayload:
    name: str
    title: str
    email: str
    phone: str
    location: str
    summary: str
    skills: tuple[str, ...]
    website: str
    telegram: str
    linkedin: str
    github: str
    about_text: str
    fingerprint: str


def _read_about_from_md() -> str:
    if not RESUME_MD.exists():
        return ""
    text = RESUME_MD.read_text(encoding="utf-8")
    match = re.search(r"## О себе\s*\n\n([\s\S]*?)\n\n## ", text)
    if not match:
        return ""
    return match.group(1).strip()


def load_resume_payload() -> ResumePayload:
    if not RESUME_JSON.exists():
        raise FileNotFoundError(f"Resume source missing: {RESUME_JSON}")

    data: dict[str, Any] = json.loads(RESUME_JSON.read_text(encoding="utf-8"))
    links = data.get("links") or {}
    skills = tuple(str(s).strip() for s in data.get("skills", []) if str(s).strip())
    about = _read_about_from_md() or str(data.get("summary", "")).strip()

    canonical = {
        "title": data.get("title", ""),
        "summary": data.get("summary", ""),
        "skills": list(skills),
        "about_text": about,
        "location": data.get("location", ""),
    }
    fingerprint = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    return ResumePayload(
        name=str(data.get("name", "")),
        title=str(data.get("title", "")),
        email=str(data.get("email", "")),
        phone=str(data.get("phone", "")),
        location=str(data.get("location", "")),
        summary=str(data.get("summary", "")),
        skills=skills,
        website=str(links.get("website", "")),
        telegram=str(links.get("telegram", "")),
        linkedin=str(links.get("linkedin", "")),
        github=str(links.get("github", "")),
        about_text=about,
        fingerprint=fingerprint,
    )


def hh_description(payload: ResumePayload) -> str:
    """About block for HH.ru (plain text + links)."""
    lines = [payload.about_text or payload.summary, ""]
    if payload.website:
        lines.append(f"Сайт и резюме: {payload.website}")
    if payload.telegram:
        lines.append(f"Telegram: {payload.telegram}")
    if payload.github:
        lines.append(f"GitHub: {payload.github}")
    return "\n".join(lines).strip()
