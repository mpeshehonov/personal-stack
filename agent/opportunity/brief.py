"""Daily Opportunity Brief for Telegram."""

from __future__ import annotations

from typing import Any

from opportunity.actions import action_label_ru
from opportunity.ideas import build_strategic_ideas
from opportunity.metrics import compute_funnel_snapshot
from opportunity.models import OpportunityStatus
from opportunity.repository import list_opportunities


def format_opportunity_brief(
    *,
    top_n: int = 5,
    actions_n: int = 3,
) -> str:
    top = list_opportunities(
        status=OpportunityStatus.NEW.value,
        opp_type="JOB",
        limit=top_n,
        min_overall=60,
    )
    # Also include high-scoring SAVED waiting for apply
    saved = list_opportunities(
        status=OpportunityStatus.SAVED.value,
        opp_type="JOB",
        limit=3,
        min_overall=70,
    )

    lines: list[str] = ["📡 Opportunity Brief", "", "🔥 Top opportunities", ""]

    if not top:
        lines.append("Нет новых JOB с overall ≥ 60. Запусти /jobs scan.")
        lines.append("")
    else:
        for i, opp in enumerate(top, 1):
            lines.extend(_format_opp_block(i, opp))

    lines.append("📌 Today’s actions")
    lines.append("")
    actions = _pick_todays_actions(top + saved, limit=actions_n)
    if not actions:
        lines.append("1. Запусти скан и разбери top-5")
    else:
        for i, text in enumerate(actions, 1):
            lines.append(f"{i}. {text}")

    # One strategic idea
    ideas = build_strategic_ideas()
    if ideas:
        idea = ideas[0]
        lines.extend(
            [
                "",
                "💡 Idea (не вакансия)",
                f"• {idea['title']}",
                f"  Почему: {idea['why'][0]}",
            ]
        )

    funnel = compute_funnel_snapshot()
    lines.extend(
        [
            "",
            "📊 Funnel",
            f"New: {funnel.get('new', 0)}",
            f"Saved: {funnel.get('saved', 0)}",
            f"Applied: {funnel.get('applied', 0)}",
            f"Interview: {funnel.get('interview', 0)}",
            f"Offer: {funnel.get('offer', 0)}",
            "",
            "Кнопки в /jobs: Ок / Мимо / Сопровод. "
            "Paywall Hirify: /jobs dislike <id> paywall — источник не штрафуем.",
        ]
    )
    return "\n".join(lines)


def _format_opp_block(index: int, opp: Any) -> list[str]:
    scores = opp.scores or {}
    fit = scores.get("fit") or {}
    prob = scores.get("probability") or {}
    why = list(fit.get("reasons") or [])[:2]
    risks = list(prob.get("reasons") or [])[:2]
    company = opp.company_or_entity or "—"
    lead = f"lead #{opp.job_lead_id}" if opp.job_lead_id else f"opp #{opp.id}"
    lines = [
        f"{index}. {company} / {opp.title}",
        f"Score: {opp.overall_score} ({lead}, {opp.source})",
        "",
        "Почему:",
    ]
    for w in why or ["см. match"]:
        lines.append(f"• {w}")
    lines.append("")
    lines.append("Риски:")
    for r in risks or ["—"]:
        lines.append(f"• {r}")
    lines.append("")
    lines.append(
        f"Следующее действие: {action_label_ru(opp.next_action)} "
        f"[{opp.next_action_priority}]"
    )
    lines.append("")
    return lines


def _pick_todays_actions(opps: list[Any], *, limit: int = 3) -> list[str]:
    ranked = sorted(
        opps,
        key=lambda o: (
            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(
                o.next_action_priority, 9
            ),
            -int(o.overall_score or 0),
        ),
    )
    out: list[str] = []
    for opp in ranked:
        if len(out) >= limit:
            break
        company = opp.company_or_entity or opp.title[:40]
        out.append(
            f"{action_label_ru(opp.next_action)} — {company} "
            f"(score {opp.overall_score})"
        )
    return out


def format_brief_digest_extra(*, exclude_ids: set[int] | None = None) -> str:
    """Short digest for remaining new jobs not in top brief."""
    exclude_ids = exclude_ids or set()
    rest = [
        o
        for o in list_opportunities(
            status=OpportunityStatus.NEW.value, opp_type="JOB", limit=20, min_overall=50
        )
        if o.id not in exclude_ids
    ][5:]
    if not rest:
        return ""
    lines = ["📦 Остальные new (digest):"]
    for o in rest[:10]:
        lines.append(
            f"• #{o.job_lead_id or o.id} {o.company_or_entity or '—'} / "
            f"{o.title[:50]} ({o.overall_score})"
        )
    return "\n".join(lines)
