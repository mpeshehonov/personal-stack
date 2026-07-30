"""Two-stage scoring: Stage A deterministic filter, Stage B personal components."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from job_hunt.matcher import score_vacancy
from opportunity.models import SCORE_KEYS, ScoreBundle, ScoreComponent
from opportunity.profile import DEFAULT_WEIGHTS, load_profile


def _clamp(n: float) -> int:
    return max(0, min(100, int(round(n))))


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def stage_a_filter(
    vacancy: dict[str, Any],
    *,
    resume_skills: list[str] | None = None,
    min_match: int = 70,
) -> tuple[bool, int, list[str]]:
    """Reuse matcher. Returns (pass, match_score, reasons)."""
    score, reasons = score_vacancy(vacancy, resume_skills=resume_skills)
    return score >= min_match, score, reasons


def _salary_income_score(
    vacancy: dict[str, Any],
    profile: dict[str, Any],
) -> ScoreComponent:
    reasons: list[str] = []
    salary = vacancy.get("salary") or {}
    amount = salary.get("from")
    if amount is None:
        amount = salary.get("to")
    currency = (salary.get("currency") or "").upper()
    min_rub = int(profile.get("min_income_rub_month") or 200000)
    min_usd = int(profile.get("min_income_usd_month") or 3000)
    target_usd = int(profile.get("target_income_usd_month") or 3500)

    if amount is None:
        return ScoreComponent(55, ["вилка не указана — нейтрально"])

    amount = int(amount)
    if currency in ("RUR", "RUB"):
        if amount >= min_rub * 1.25:
            return ScoreComponent(90, [f"вилка от {amount} RUB ≥ цель"])
        if amount >= min_rub:
            return ScoreComponent(78, [f"вилка от {amount} RUB ок"])
        if amount >= int(min_rub * 0.75):
            return ScoreComponent(45, [f"вилка {amount} RUB ниже минимума"])
        return ScoreComponent(20, [f"вилка {amount} RUB слишком низкая"])

    if currency == "USD":
        if amount >= target_usd:
            return ScoreComponent(92, [f"${amount}/mo на цели"])
        if amount >= min_usd:
            return ScoreComponent(80, [f"${amount}/mo ≥ минимум"])
        return ScoreComponent(35, [f"${amount}/mo ниже минимума"])

    reasons.append(f"валюта {currency or '?'} — осторожно")
    return ScoreComponent(50, reasons)


def _fit_score(
    vacancy: dict[str, Any],
    match_score: int,
    match_reasons: list[str],
    profile: dict[str, Any],
) -> ScoreComponent:
    reasons = list(match_reasons[:4])
    title = _norm(vacancy.get("name") or "")
    blob = _norm(
        " ".join(
            [
                vacancy.get("name") or "",
                str((vacancy.get("snippet") or {}).get("requirement") or ""),
                str((vacancy.get("snippet") or {}).get("responsibility") or ""),
            ]
        )
    )
    score = float(match_score)

    undesired = [_norm(x) for x in (profile.get("undesired") or [])]
    for u in undesired:
        if u and u.replace("_", " ") in blob:
            score -= 12
            reasons.append(f"нежелательно: {u}")

    # Vue/Angular primary without React
    if ("vue" in blob or "nuxt" in blob) and "react" not in blob:
        score -= 20
        reasons.append("Vue/Nuxt без React (−20)")
    if "angular" in blob and "react" not in blob:
        score -= 20
        reasons.append("Angular primary (−20)")

    # Adjacent RN boost if in interests
    interests = " ".join(_norm(x) for x in (profile.get("strategic_interests") or []))
    if "react native" in blob or "expo" in blob:
        if "react native" in interests or "expo" in interests:
            score += 8
            reasons.append("adjacent RN/Expo в интересах (+8)")
        else:
            score -= 5
            reasons.append("RN/mobile — не основной трек (−5)")

    for role in profile.get("target_roles") or []:
        rn = _norm(role)
        if rn and any(tok in title for tok in rn.split() if len(tok) > 3):
            score += 5
            reasons.append(f"близко к целевой роли ({role})")
            break

    return ScoreComponent(_clamp(score), reasons)


def _growth_score(vacancy: dict[str, Any], profile: dict[str, Any]) -> ScoreComponent:
    blob = _norm(
        " ".join(
            [
                vacancy.get("name") or "",
                str((vacancy.get("snippet") or {}).get("responsibility") or ""),
            ]
        )
    )
    reasons: list[str] = []
    score = 50
    growth_kw = (
        "lead",
        "архитект",
        "platform",
        "design system",
        "ownership",
        "module federation",
        "greenfield",
        "с нуля",
        "ответственност",
    )
    hits = [k for k in growth_kw if k in blob]
    if hits:
        score += min(25, 8 * len(hits))
        reasons.append(f"рост: {', '.join(hits[:3])}")
    interests = profile.get("strategic_interests") or []
    for interest in interests:
        token = _norm(interest).split("/")[0].strip()
        if len(token) >= 4 and token in blob:
            score += 10
            reasons.append(f"стратегический интерес: {interest}")
            break
    if not reasons:
        reasons.append("обычный senior FE scope")
    return ScoreComponent(_clamp(score), reasons)


def _probability_score(
    vacancy: dict[str, Any],
    *,
    match_score: int,
) -> ScoreComponent:
    """Chance of progress: actionability + freshness + company clarity."""
    reasons: list[str] = []
    score = 55.0
    source = _norm(str(vacancy.get("_source") or ""))
    company = (vacancy.get("employer") or {}).get("name") or vacancy.get("company") or ""
    company = str(company).strip()

    actionable = vacancy.get("_actionable")
    if actionable is False or vacancy.get("_paywall"):
        score -= 35
        reasons.append("низкая actionability (paywall / нет контактов)")
    elif source == "hirify":
        # Hirify cards often need Plus for contacts
        score -= 18
        reasons.append("Hirify: контакты часто за Plus (−18 probability)")
        if not company:
            score -= 10
            reasons.append("Hirify без названия компании (−10)")
    elif company:
        score += 8
        reasons.append("компания указана (+8)")

    if vacancy.get("alternate_url") and "hh.ru" in str(vacancy.get("alternate_url")):
        score += 10
        reasons.append("прямой отклик на HH (+10)")

    # Freshness
    age_days = _vacancy_age_days(vacancy)
    if age_days is not None:
        if age_days <= 3:
            score += 12
            reasons.append(f"свежая ({age_days}д) (+12)")
        elif age_days <= 14:
            score += 4
            reasons.append(f"возраст {age_days}д (+4)")
        elif age_days <= 30:
            score -= 8
            reasons.append(f"висит {age_days}д (−8)")
        else:
            score -= 20
            reasons.append(f"устарела ~{age_days}д (−20)")

    # Strong match → slightly higher conversion hope
    if match_score >= 85:
        score += 5
        reasons.append("сильный fit (+5 probability)")

    return ScoreComponent(_clamp(score), reasons)


def _vacancy_age_days(vacancy: dict[str, Any]) -> int | None:
    raw = (
        vacancy.get("_published_at")
        or vacancy.get("published_at")
        or vacancy.get("created_at")
    )
    if not raw:
        return None
    try:
        text = str(raw).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except ValueError:
        return None


def _strategic_score(vacancy: dict[str, Any], profile: dict[str, Any]) -> ScoreComponent:
    reasons: list[str] = []
    score = 45.0
    blob = _norm(
        " ".join(
            [
                vacancy.get("name") or "",
                (vacancy.get("employer") or {}).get("name") or "",
                str((vacancy.get("snippet") or {}).get("responsibility") or ""),
            ]
        )
    )
    company_types = [_norm(x) for x in (profile.get("desired_company_types") or [])]
    for ct in company_types:
        if ct and ct in blob:
            score += 12
            reasons.append(f"тип компании: {ct}")
            break

    # Brand / enterprise stability
    brands = ("x5", "тинькофф", "т-банк", "ozon", "avito", "yandex", "яндекс", "сбер", "vk ")
    if any(b in blob for b in brands):
        score += 10
        reasons.append("узнаваемый бренд (+10)")

    if "remote" in blob or "удал" in blob:
        score += 8
        reasons.append("remote совпадает с целью (+8)")

    if profile.get("remote_preference") == "remote_only":
        office = ("#офис" in blob) or ("офис" in blob and "удал" not in blob)
        if office and "remote" not in blob:
            score -= 25
            reasons.append("офис при remote_only (−25)")

    if not reasons:
        reasons.append("нейтральная стратегия")
    return ScoreComponent(_clamp(score), reasons)


def _urgency_score(vacancy: dict[str, Any], profile: dict[str, Any]) -> ScoreComponent:
    reasons: list[str] = []
    score = 50.0
    # RED mode / asap from profile goals
    goals = " ".join(_norm(g) for g in (profile.get("career_goals") or []))
    if "asap" in goals or "стабил" in goals:
        score += 10
        reasons.append("цель: стабилизация дохода (+10 urgency)")

    age = _vacancy_age_days(vacancy)
    if age is not None and age <= 2:
        score += 15
        reasons.append("только появилась (+15)")
    elif age is not None and age > 21:
        score -= 15
        reasons.append("давно висит — срочность низкая (−15)")

    if vacancy.get("_paywall") or vacancy.get("_actionable") is False:
        score -= 20
        reasons.append("нельзя быстро откликнуться (−20)")

    if not reasons:
        reasons.append("обычная срочность")
    return ScoreComponent(_clamp(score), reasons)


def compute_overall(components: dict[str, ScoreComponent], weights: dict[str, float]) -> int:
    """Deterministic weighted average; LLM must not set this directly."""
    w = dict(DEFAULT_WEIGHTS)
    w.update(weights or {})
    total_w = sum(w.get(k, 0.0) for k in SCORE_KEYS) or 1.0
    acc = 0.0
    for key in SCORE_KEYS:
        acc += components[key].score * (w.get(key, 0.0) / total_w)
    return _clamp(acc)


def score_opportunity(
    vacancy: dict[str, Any],
    *,
    match_score: int,
    match_reasons: list[str] | None = None,
    profile: dict[str, Any] | None = None,
) -> ScoreBundle:
    profile = profile or load_profile()
    match_reasons = match_reasons or []
    # Preference adjustments (slow, explainable)
    adj = profile.get("preference_adjustments") or {}
    weights = dict(profile.get("score_weights") or DEFAULT_WEIGHTS)
    for key, delta in (adj.get("weight_deltas") or {}).items():
        if key in weights:
            weights[key] = max(0.05, min(0.5, weights[key] + float(delta)))

    components = {
        "fit": _fit_score(vacancy, match_score, match_reasons, profile),
        "income": _salary_income_score(vacancy, profile),
        "growth": _growth_score(vacancy, profile),
        "probability": _probability_score(vacancy, match_score=match_score),
        "strategic": _strategic_score(vacancy, profile),
        "urgency": _urgency_score(vacancy, profile),
    }

    # Feature boosts from preference model (bounded)
    feature_boosts = adj.get("feature_boosts") or {}
    blob = _norm(str(vacancy.get("name") or "") + " " + str(vacancy.get("_source") or ""))
    for feature, boost in feature_boosts.items():
        if _norm(feature) in blob:
            components["fit"] = ScoreComponent(
                _clamp(components["fit"].score + float(boost)),
                components["fit"].reasons + [f"preference «{feature}» ({boost:+.0f})"],
            )

    overall = compute_overall(components, weights)
    return ScoreBundle(
        fit=components["fit"],
        income=components["income"],
        growth=components["growth"],
        probability=components["probability"],
        strategic=components["strategic"],
        urgency=components["urgency"],
        overall=overall,
        weights=weights,
    )


def lead_row_to_vacancy_shape(row: Any) -> dict[str, Any]:
    """Rebuild HH-like dict from job_leads row for rescoring."""
    import json

    skills = []
    try:
        skills = json.loads(row["skills_json"] or "[]")
    except (TypeError, json.JSONDecodeError, KeyError):
        skills = []
    salary = None
    try:
        raw = row["salary_raw"]
        if raw:
            salary = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError, KeyError):
        salary = None

    source = row["source"] if hasattr(row, "keys") else row.get("source")
    return {
        "id": row["external_id"],
        "name": row["title"],
        "alternate_url": row["url"],
        "employer": {"name": row["company"] or ""},
        "key_skills": [{"name": s} for s in skills],
        "salary": salary,
        "snippet": {
            "requirement": row["description_snippet"] or "",
            "responsibility": "",
        },
        "area": {"name": row["location"] or ""},
        "schedule": {
            "id": "remote" if "удал" in _norm(row["location"] or "") else "",
            "name": row["location"] or "",
        },
        "_source": source,
        "_published_at": row["ts"] if "ts" in row.keys() else None,
        "_actionable": source != "hirify",
        "_paywall": source == "hirify",
    }
