"""Score HH.ru vacancies against resume.json skills and title keywords."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from job_hunt.config import JOBHUNT_MIN_SALARY_RUB
from orchestrator.config import SITE_DIR

RESUME_PATH = SITE_DIR / "content" / "resume" / "resume.json"

TITLE_KEYWORDS = (
    "senior",
    "lead",
    "frontend",
    "front-end",
    "react",
    "next",
    "next.js",
    "nextjs",
)

SPAM_KEYWORDS = (
    "аутстафф",
    "outstaff",
    "outsource",
    "staffing",
    "mass hiring",
    "массовый набор",
    "курсы",
    "обучение с трудоустройством",
)

REMOTE_SCHEDULE_IDS = frozenset({"remote", "flyInFlyOut"})
HYBRID_KEYWORDS = ("гибрид", "hybrid", "частично удал")


def load_resume_skills() -> list[str]:
    if not RESUME_PATH.exists():
        return []
    data = json.loads(RESUME_PATH.read_text(encoding="utf-8"))
    return [str(s).strip() for s in data.get("skills", []) if str(s).strip()]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _salary_min_rub(salary: dict[str, Any] | None) -> int | None:
    if not salary:
        return None
    currency = (salary.get("currency") or "").upper()
    amount = salary.get("from")
    if amount is None:
        return None
    if currency in ("RUR", "RUB"):
        return int(amount)
    return None


def _collect_skill_names(vacancy: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for item in vacancy.get("key_skills") or []:
        if name := item.get("name"):
            names.add(_normalize(name))
    snippet = " ".join(
        filter(
            None,
            [
                (vacancy.get("snippet") or {}).get("requirement"),
                (vacancy.get("snippet") or {}).get("responsibility"),
            ],
        )
    )
    if snippet:
        names.update(_normalize(snippet).split())
    return names


def score_vacancy(vacancy: dict[str, Any], *, resume_skills: list[str] | None = None) -> tuple[int, list[str]]:
    """Return (match_score 0–100, human-readable reasons)."""
    resume_skills = resume_skills if resume_skills is not None else load_resume_skills()
    reasons: list[str] = []
    score = 0

    title = _normalize(vacancy.get("name") or "")
    description = _normalize(
        " ".join(
            filter(
                None,
                [
                    title,
                    (vacancy.get("snippet") or {}).get("requirement"),
                    (vacancy.get("snippet") or {}).get("responsibility"),
                ],
            )
        )
    )

    if any(kw in title for kw in TITLE_KEYWORDS):
        score += 25
        reasons.append("title keyword match (+25)")

    vacancy_skills = _collect_skill_names(vacancy)
    overlap = 0
    matched: list[str] = []
    for skill in resume_skills:
        norm = _normalize(skill)
        if norm in vacancy_skills or norm in description or norm.replace(".", "") in description:
            overlap += 1
            matched.append(skill)
    skill_points = min(overlap * 5, 40)
    if skill_points:
        score += skill_points
        preview = ", ".join(matched[:5])
        if len(matched) > 5:
            preview += f" +{len(matched) - 5}"
        reasons.append(f"skills overlap {len(matched)} (+{skill_points}): {preview}")

    schedule = vacancy.get("schedule") or {}
    schedule_id = (schedule.get("id") or "").lower()
    schedule_name = _normalize(schedule.get("name") or "")
    if schedule_id in REMOTE_SCHEDULE_IDS or "удал" in schedule_name or "remote" in schedule_name:
        score += 10
        reasons.append("remote (+10)")
    elif any(kw in schedule_name or kw in description for kw in HYBRID_KEYWORDS):
        score += 10
        reasons.append("hybrid (+10)")

    salary_min = _salary_min_rub(vacancy.get("salary"))
    if salary_min is not None and salary_min >= JOBHUNT_MIN_SALARY_RUB:
        score += 10
        reasons.append(f"salary min {salary_min:,} RUB (+10)".replace(",", " "))

    if any(kw in description for kw in SPAM_KEYWORDS):
        score -= 30
        reasons.append("spam/agency keyword (−30)")

    return max(0, min(100, score)), reasons
