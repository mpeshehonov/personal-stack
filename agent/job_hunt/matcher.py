"""Score vacancies against Senior Product / Frontend Engineer bar."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from job_hunt.config import JOBHUNT_MIN_SALARY_RUB, JOBHUNT_MIN_SALARY_USD
from orchestrator.config import SITE_DIR

RESUME_PATH = SITE_DIR / "content" / "resume" / "resume.json"

SENIOR_TITLE_KEYWORDS = (
    "senior",
    "lead",
    "staff",
    "principal",
    "product engineer",
    "старш",
    "ведущ",
)

PRODUCT_TITLE_KEYWORDS = (
    "product",
    "frontend",
    "front-end",
    "front end",
    "react",
    "next.js",
    "nextjs",
    "фронтенд",
    "фронт",
)

CORE_STACK = (
    "react",
    "typescript",
    "javascript",
    "next.js",
    "nextjs",
    "redux",
    "mobx",
    "tanstack",
    "react query",
    "graphql",
    "rest",
)

HARD_SPAM = (
    "без опыта",
    "без коммерческого",
    "стажёр",
    "стажер",
    "intern",
    "junior",
    "джуниор",
    "курсы с трудоустройством",
    "обучение с трудоустройством",
    "массовый набор",
    "mass hiring",
)

WEAK_OR_MISMATCH = (
    "верстальщик",
    "html/css верстка",
    "только верстка",
    "bitrix",
    "1c-bitrix",
    "1с-битрикс",
    "jquery",
    "oracle apex",
    "xbpm",
    "x-bpm",
    "apex",
    "1с ",
    "1c developer",
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


def _salary_amounts(salary: dict[str, Any] | None) -> tuple[int | None, str | None]:
    if not salary:
        return None, None
    currency = (salary.get("currency") or "").upper()
    amount = salary.get("from")
    if amount is None:
        amount = salary.get("to")
    if amount is None:
        return None, None
    return int(amount), currency


def _collect_blob(vacancy: dict[str, Any]) -> str:
    title = vacancy.get("name") or ""
    snippet = vacancy.get("snippet") or {}
    skills = " ".join(
        s.get("name") or "" for s in (vacancy.get("key_skills") or []) if s.get("name")
    )
    return _normalize(
        " ".join(
            filter(
                None,
                [
                    title,
                    snippet.get("requirement"),
                    snippet.get("responsibility"),
                    skills,
                ],
            )
        )
    )


def score_vacancy(
    vacancy: dict[str, Any], *, resume_skills: list[str] | None = None
) -> tuple[int, list[str]]:
    """Return (match_score 0–100, short RU reasons for Telegram)."""
    resume_skills = resume_skills if resume_skills is not None else load_resume_skills()
    reasons: list[str] = []
    score = 40  # baseline for any FE-ish remote scan item

    title = _normalize(vacancy.get("name") or "")
    blob = _collect_blob(vacancy)

    if any(kw in blob for kw in HARD_SPAM):
        return 0, ["отсев: junior/стажёр/без опыта"]

    # Hard mismatch roles (unless React clearly present for edge cases)
    mismatch_hits = [kw for kw in WEAK_OR_MISMATCH if kw in blob]
    reactish = any(k in blob for k in ("react", "typescript", "next.js", "nextjs"))
    if mismatch_hits and not reactish:
        return 5, [f"отсев: не наш стек ({mismatch_hits[0]})"]
    if mismatch_hits and reactish and any(
        k in mismatch_hits for k in ("oracle apex", "xbpm", "x-bpm", "apex")
    ):
        score -= 25
        reasons.append(f"минус: смещение в {mismatch_hits[0]} (−25)")

    if any(kw in title for kw in SENIOR_TITLE_KEYWORDS):
        score += 20
        reasons.append("senior/lead в названии (+20)")
    elif "middle" in title or "мидл" in title:
        score -= 15
        reasons.append("middle в названии (−15)")

    if any(kw in title for kw in PRODUCT_TITLE_KEYWORDS):
        score += 15
        reasons.append("product/frontend/react в названии (+15)")

    stack_hits = [k for k in CORE_STACK if k in blob]
    stack_points = min(len(set(stack_hits)) * 4, 20)
    if stack_points:
        score += stack_points
        reasons.append(f"стек overlap (+{stack_points})")

    overlap = 0
    matched: list[str] = []
    for skill in resume_skills:
        norm = _normalize(skill)
        if not norm:
            continue
        if norm in blob or norm.replace(".", "") in blob:
            overlap += 1
            matched.append(skill)
    skill_points = min(overlap * 3, 15)
    if skill_points:
        score += skill_points
        preview = ", ".join(matched[:4])
        reasons.append(f"навыки резюме (+{skill_points}): {preview}")

    schedule = vacancy.get("schedule") or {}
    schedule_id = (schedule.get("id") or "").lower()
    schedule_name = _normalize(schedule.get("name") or "")
    if (
        schedule_id in REMOTE_SCHEDULE_IDS
        or "удал" in schedule_name
        or "remote" in schedule_name
        or "удал" in blob
        or "remote" in blob
    ):
        score += 10
        reasons.append("remote (+10)")
    elif any(kw in schedule_name or kw in blob for kw in HYBRID_KEYWORDS):
        score += 6
        reasons.append("hybrid (+6)")
    else:
        score -= 8
        reasons.append("не remote (−8)")

    amount, currency = _salary_amounts(vacancy.get("salary"))
    if amount is not None and currency:
        if currency in ("RUR", "RUB") and amount >= JOBHUNT_MIN_SALARY_RUB:
            score += 12
            reasons.append(f"вилка от {amount} RUB (+12)")
        elif currency == "USD" and amount >= JOBHUNT_MIN_SALARY_USD:
            score += 12
            reasons.append(f"вилка от ${amount} (+12)")
        elif currency in ("RUR", "RUB") and amount < 150000:
            score -= 10
            reasons.append(f"низкая вилка {amount} RUB (−10)")

    agency = ("аутстафф", "outstaff", "staffing", "аутсорс набор")
    if any(kw in blob for kw in agency):
        score -= 12
        reasons.append("аутстафф/agency (−12)")

    return max(0, min(100, score)), reasons
