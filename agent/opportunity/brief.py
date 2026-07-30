"""Daily Opportunity Brief for Telegram — action-first, Russian UX."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from opportunity.actions import action_how_ru, action_label_ru
from opportunity.ideas import build_strategic_ideas
from opportunity.metrics import compute_funnel_snapshot
from opportunity.models import OpportunityStatus
from opportunity.repository import list_opportunities


def build_opportunity_brief(
    *,
    top_n: int = 5,
    actions_n: int = 3,
) -> dict[str, Any]:
    """Structured brief: header text + card payloads for inline keyboards."""
    top = _select_top_jobs(limit=top_n)
    saved = list_opportunities(
        status=OpportunityStatus.SAVED.value,
        opp_type="JOB",
        limit=5,
        min_overall=65,
    )
    applied = list_opportunities(
        status=OpportunityStatus.APPLIED.value,
        opp_type="JOB",
        limit=10,
        min_overall=0,
    )
    followups = _select_followups(applied)

    header = _format_header(top, saved, followups, actions_n=actions_n)
    cards = [_card_payload(opp) for opp in top]
    digest = _format_digest(exclude_ids={c["opportunity_id"] for c in cards if c.get("opportunity_id")})
    followup_text = _format_followups(followups)

    return {
        "header": header,
        "cards": cards,
        "followup_text": followup_text,
        "digest": digest,
    }


def format_opportunity_brief(
    *,
    top_n: int = 5,
    actions_n: int = 3,
) -> str:
    """Plain-text fallback (tests / logs). Prefer build_opportunity_brief in Telegram."""
    data = build_opportunity_brief(top_n=top_n, actions_n=actions_n)
    parts = [data["header"]]
    if data["cards"]:
        parts.append("")
        parts.append("Карточки (в Telegram под ними кнопки):")
        for i, card in enumerate(data["cards"], 1):
            parts.append(f"{i}. {card['text'].splitlines()[0]}")
    if data.get("followup_text"):
        parts.extend(["", data["followup_text"]])
    if data.get("digest"):
        parts.extend(["", data["digest"]])
    return "\n".join(parts)


def format_brief_digest_extra(*, exclude_ids: set[int] | None = None) -> str:
    return _format_digest(exclude_ids=exclude_ids or set())


def _select_top_jobs(*, limit: int) -> list[Any]:
    candidates = list_opportunities(
        status=OpportunityStatus.NEW.value,
        opp_type="JOB",
        limit=40,
        min_overall=60,
    )
    ranked = sorted(candidates, key=lambda o: (_brief_rank_key(o), -int(o.overall_score or 0)))
    return ranked[:limit]


def _brief_rank_key(opp: Any) -> tuple:
    """Lower is better. Soft-demote middle / RN-only / agency noise in brief."""
    title = (opp.title or "").lower()
    company = (opp.company_or_entity or "").lower()
    penalty = 0
    if "middle" in title or "мидл" in title:
        penalty += 2
    if "react native" in title and "frontend" not in title.replace("react native", ""):
        penalty += 1
    if any(x in company for x in ("recruit", "hireway", "hire feed", "resource solution", "jit team")):
        penalty += 2
    if (opp.analysis or {}).get("paywall"):
        penalty += 1
    return (penalty,)


def _select_followups(applied: list[Any]) -> list[Any]:
    """Applied with silence — show for follow-up after ~3 days."""
    out = []
    now = datetime.now(timezone.utc)
    for opp in applied:
        age = _days_since(opp.updated_at or opp.created_at)
        if age is None or age >= 3:
            out.append(opp)
    return out[:5]


def _days_since(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        text = str(iso).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except ValueError:
        return None


def _format_header(
    top: list[Any],
    saved: list[Any],
    followups: list[Any],
    *,
    actions_n: int,
) -> str:
    lines = [
        "📡 Бриф возможностей",
        "",
        "Как работать с брифом:",
        "1) Под каждой вакансией кнопки — не копируй id руками",
        "2) «Открыть» → отклик на сайте → «Откликнулся»",
        "3) Не то → «Мимо». Сомнительно → «В избранное»",
        "4) Уже откликался снаружи → всё равно жми «Откликнулся», иначе воронка врёт",
        "",
    ]

    if followups:
        lines.append("⚠ Тишина после отклика — сначала это:")
        for i, opp in enumerate(followups[:actions_n], 1):
            days = _days_since(opp.updated_at or opp.created_at)
            days_s = f"{days}д" if days is not None else "?"
            lead = opp.job_lead_id or opp.id
            lines.append(
                f"{i}) Написать follow-up по #{lead} "
                f"{opp.company_or_entity or '—'} (тишина {days_s})"
            )
        lines.append("   Как: письмо/чат рекрутеру или повторный контакт в HH. Потом жди.")
        lines.append("")

    lines.append("📌 На сегодня (новые):")
    if not top:
        lines.append("• Новых сильных нет — жми Скан или разбери избранное")
    else:
        for i, opp in enumerate(top[:actions_n], 1):
            lead = opp.job_lead_id or opp.id
            how = action_how_ru(opp.next_action)
            lines.append(
                f"{i}) #{lead} {opp.company_or_entity or '—'} — {how}"
            )
    lines.append("")

    idea = (build_strategic_ideas() or [None])[0]
    if idea:
        lines.extend(
            [
                "💡 Кроме вакансий (простыми словами)",
                f"• {idea['title']}",
            ]
        )
        for step in idea.get("steps") or idea.get("why") or []:
            lines.append(f"  — {step}")
        lines.append("")

    funnel = compute_funnel_snapshot()
    lines.extend(
        [
            "📊 Воронка",
            f"Новые: {funnel.get('new', 0)}",
            f"В избранном: {funnel.get('saved', 0)}",
            f"Отклики: {funnel.get('applied', 0)}",
            f"Собеседования: {funnel.get('interview', 0)}",
            f"Офферы: {funnel.get('offer', 0)}",
            "",
            "Карточки top ↓",
        ]
    )
    return "\n".join(lines)


def _card_payload(opp: Any) -> dict[str, Any]:
    scores = opp.scores or {}
    fit = scores.get("fit") or {}
    prob = scores.get("probability") or {}
    why = list(fit.get("reasons") or [])[:2]
    risks = _negative_reasons(prob.get("reasons") or [])
    lead_id = opp.job_lead_id
    company = opp.company_or_entity or "—"
    lines = [
        f"#{lead_id or opp.id} · {opp.overall_score} баллов · {opp.source}",
        f"{company}",
        opp.title or "—",
        "",
        f"Что сделать: {action_how_ru(opp.next_action)}",
    ]
    if why:
        lines.append("Почему в топе: " + "; ".join(why))
    if risks:
        lines.append("Риски: " + "; ".join(risks))
    elif (opp.analysis or {}).get("paywall"):
        lines.append("Риски: контакты могут быть за paywall — ищи компанию в LinkedIn/HH")

    return {
        "opportunity_id": opp.id,
        "lead_id": lead_id,
        "url": opp.source_url or "",
        "text": "\n".join(lines),
    }


def _negative_reasons(reasons: list[str]) -> list[str]:
    bad_tokens = (
        "−",
        "-",
        "низк",
        "paywall",
        "plus",
        "устарел",
        "висит",
        "нет контакт",
        "actionability",
        "офис",
        "без названия",
    )
    out = []
    for r in reasons:
        low = r.lower()
        if any(t in low for t in bad_tokens) or "(-" in r:
            out.append(r)
    return out[:2]


def _format_followups(followups: list[Any]) -> str:
    if not followups:
        return ""
    lines = [
        "🔁 Follow-up (отклик был, ответа нет)",
        "Не открывай новые пачками, пока не пинганёшь эти.",
    ]
    for opp in followups:
        days = _days_since(opp.updated_at or opp.created_at)
        lines.append(
            f"• #{opp.job_lead_id or opp.id} {opp.company_or_entity or '—'} / "
            f"{(opp.title or '')[:40]} — тишина {days if days is not None else '?'}д"
            + (f"\n  {opp.source_url}" if opp.source_url else "")
        )
    return "\n".join(lines)


def _format_digest(*, exclude_ids: set[int]) -> str:
    rest = [
        o
        for o in list_opportunities(
            status=OpportunityStatus.NEW.value, opp_type="JOB", limit=25, min_overall=50
        )
        if o.id not in exclude_ids
    ][5:]
    if not rest:
        return ""
    lines = ["📦 Ещё новые (без кнопок — открой /jobs или #id):"]
    for o in rest[:8]:
        lines.append(
            f"• #{o.job_lead_id or o.id} {o.company_or_entity or '—'} / "
            f"{(o.title or '')[:45]} ({o.overall_score})"
        )
    return "\n".join(lines)
