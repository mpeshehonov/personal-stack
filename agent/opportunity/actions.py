"""Next-action engine — concrete action + priority from status/scores."""

from __future__ import annotations

from typing import Any

from opportunity.models import ActionPriority, NextAction, OpportunityStatus


def decide_next_action(
    *,
    status: str | OpportunityStatus,
    scores: dict[str, Any] | None = None,
    analysis: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Return (next_action, priority)."""
    status_val = status.value if isinstance(status, OpportunityStatus) else str(status)
    scores = scores or {}
    analysis = analysis or {}
    overall = int(scores.get("overall_score") or 0)
    probability = int((scores.get("probability") or {}).get("score") or 50)
    actionable = analysis.get("actionable", True)
    paywall = bool(analysis.get("paywall"))
    strategy = str(analysis.get("apply_strategy") or "")

    if status_val in (
        OpportunityStatus.ARCHIVED.value,
        OpportunityStatus.SKIPPED.value,
        OpportunityStatus.REJECTED.value,
    ):
        return NextAction.ARCHIVE.value, ActionPriority.LOW.value

    if status_val == OpportunityStatus.HIRED.value:
        return NextAction.WAIT.value, ActionPriority.LOW.value

    if status_val == OpportunityStatus.OFFER.value:
        return NextAction.EVALUATE_OFFER.value, ActionPriority.CRITICAL.value

    if status_val == OpportunityStatus.INTERVIEW.value:
        return NextAction.PREPARE_INTERVIEW.value, ActionPriority.CRITICAL.value

    if status_val == OpportunityStatus.APPLIED.value:
        return NextAction.FOLLOW_UP.value, ActionPriority.MEDIUM.value

    # Prefer writing to a real contact over clicking aggregator "apply"
    if strategy in ("direct_tg", "direct_email") and status_val in (
        OpportunityStatus.NEW.value,
        OpportunityStatus.REVIEW.value,
        OpportunityStatus.SAVED.value,
        "new",
        "review",
        "saved",
    ):
        prio = ActionPriority.HIGH.value if overall >= 70 else ActionPriority.MEDIUM.value
        return NextAction.WRITE_TO_CONTACT.value, prio

    # Aggregator / paywall / no contacts → find company + direct path
    if paywall or actionable is False or strategy in ("research_company", "weak"):
        if overall >= 80:
            return NextAction.RESEARCH_COMPANY.value, ActionPriority.HIGH.value
        return NextAction.RESEARCH_COMPANY.value, ActionPriority.MEDIUM.value

    if status_val == OpportunityStatus.SAVED.value:
        if overall >= 75 and probability >= 55:
            return NextAction.APPLY.value, ActionPriority.HIGH.value
        return NextAction.REVIEW.value, ActionPriority.MEDIUM.value

    if overall >= 85 and probability >= 60:
        return NextAction.APPLY.value, ActionPriority.HIGH.value
    if overall >= 70:
        return NextAction.REVIEW.value, ActionPriority.MEDIUM.value
    return NextAction.REVIEW.value, ActionPriority.LOW.value


def action_label_ru(action: str) -> str:
    return {
        NextAction.APPLY.value: "Откликнуться",
        NextAction.REVIEW.value: "Открыть и решить",
        NextAction.WRITE_TO_CONTACT.value: "Написать контакту",
        NextAction.FOLLOW_UP.value: "Написать follow-up",
        NextAction.RESEARCH_COMPANY.value: "Найти прямой контакт",
        NextAction.PREPARE_INTERVIEW.value: "Подготовиться к интервью",
        NextAction.EVALUATE_OFFER.value: "Оценить оффер",
        NextAction.WAIT.value: "Ждать ответа",
        NextAction.ARCHIVE.value: "В архив",
        NextAction.CONSIDER_SWITCH.value: "Смежный трек (не вместо FE)",
    }.get(action, action)


def action_how_ru(action: str, analysis: dict[str, Any] | None = None) -> str:
    """One-line instruction for humans. Prefer concrete contacts when known."""
    analysis = analysis or {}
    hint = (analysis.get("apply_hint_ru") or "").strip()
    contacts = analysis.get("apply_contacts") or {}
    tgs = contacts.get("telegrams") or analysis.get("telegrams") or []
    emails = contacts.get("emails") or analysis.get("emails") or []
    urls = contacts.get("direct_urls") or analysis.get("direct_urls") or []

    if action == NextAction.WRITE_TO_CONTACT.value:
        if tgs:
            return (
                f"ЛС {', '.join(tgs[:3])} + короткий сопровод (/cover tg). "
                "Не через бота канала"
            )
        if emails:
            return f"Письмо на {', '.join(emails[:2])} + /cover email"
        if hint:
            return hint
        return "Найди рекрутера/EM и напиши коротко в ЛС/на почту"

    if action == NextAction.APPLY.value:
        if urls:
            return f"Отклик по прямой ссылке: {urls[0]} → «Откликнулся»"
        if hint and "Прямой отклик" in hint:
            return hint
        return (
            "Открой прямую ссылку (HH/карьера) → откликнись → «Откликнулся». "
            "Не через Runello/gmatch"
        )

    if action == NextAction.RESEARCH_COMPANY.value:
        if hint:
            return hint
        company = (analysis.get("company") or "").strip()
        co = f"«{company}»" if company else "компанию из вакансии"
        return (
            f"Не через Runello/gmatch/Hirify-бота. Найди {co}: сайт/карьера/HH/LinkedIn → "
            "мыло или TG HR в личку → /cover tg"
        )

    return {
        NextAction.REVIEW.value: (
            "Открой пост → глянь стек → ищи прямой контакт (не кнопку агрегатора)"
        ),
        NextAction.FOLLOW_UP.value: (
            "Тишина после отклика: пинг рекрутеру (HH/почта/TG). Не жди вечно"
        ),
        NextAction.PREPARE_INTERVIEW.value: "Собери вопросы и кейсы под компанию",
        NextAction.EVALUATE_OFFER.value: "Сравни вилку с минимумом из /profile",
        NextAction.WAIT.value: "Жди ответа, новые пачки не раздувай",
        NextAction.ARCHIVE.value: "Закрыто — не возвращайся",
        NextAction.CONSIDER_SWITCH.value: (
            "Не увольняй FE-поиск: 1 эксперимент в смежном треке на этой неделе"
        ),
    }.get(action, action_label_ru(action))
