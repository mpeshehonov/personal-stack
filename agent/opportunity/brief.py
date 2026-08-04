"""Daily Opportunity Brief for Telegram — action-first, Russian UX."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from opportunity.actions import action_how_ru, action_label_ru
from opportunity.metrics import compute_funnel_snapshot
from opportunity.models import OpportunityStatus
from opportunity.repository import list_opportunities


def build_opportunity_brief(
    *,
    top_n: int = 5,
    actions_n: int = 3,
) -> dict[str, Any]:
    """Structured brief: header + JOB cards + CLIENT/NETWORK/PRODUCT cards."""
    from opportunity.services import ensure_all_opportunities

    ensure_all_opportunities()

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

    clients = _select_vertical("CLIENT", limit=5)
    network = _select_vertical("NETWORK", limit=2)
    products = _select_vertical("PRODUCT", limit=2)

    header = _format_header(
        top,
        saved,
        followups,
        clients=clients,
        network=network,
        products=products,
        actions_n=actions_n,
    )
    cards = [_card_payload(opp) for opp in top]
    vertical_cards = (
        [_vertical_card_payload(opp, "Клиент") for opp in clients]
        + [_vertical_card_payload(opp, "Сеть") for opp in network]
        + [_vertical_card_payload(opp, "Продукт") for opp in products]
    )
    digest = _format_digest(
        exclude_ids={c["opportunity_id"] for c in cards if c.get("opportunity_id")}
    )
    followup_text = _format_followups(followups)

    return {
        "header": header,
        "cards": cards,
        "vertical_cards": vertical_cards,
        "followup_text": followup_text,
        "digest": digest,
    }


def _select_vertical(opp_type: str, *, limit: int) -> list[Any]:
    rows = list_opportunities(
        status=OpportunityStatus.NEW.value,
        opp_type=opp_type,
        limit=40,
        min_overall=40,
    )
    if opp_type == "PRODUCT":
        # Always surface ownership gate / owned package before speculative net-new
        def _prod_key(o: Any) -> tuple:
            kind = (o.analysis or {}).get("kind") or ""
            rank = {
                "ownership_gate": 0,
                "owned_package": 1,
                "net_new": 2,
            }.get(kind, 3)
            return (rank, -int(o.overall_score or 0))

        rows = sorted(rows, key=_prod_key)
    elif opp_type == "CLIENT":
        # Real freelance orders first; static retainer bridge last
        def _client_key(o: Any) -> tuple:
            kind = (o.analysis or {}).get("kind") or ""
            rank = {
                "freelance_order": 0,
                "retainer": 1,
            }.get(kind, 2)
            return (rank, -int(o.overall_score or 0))

        rows = sorted(rows, key=_client_key)
    return rows[:limit]


def _vertical_card_payload(opp: Any, label_ru: str) -> dict[str, Any]:
    steps = list((opp.analysis or {}).get("steps") or [])[:3]
    why = list((opp.scores or {}).get("strategic", {}).get("reasons") or [])[:2]
    if not why:
        why = list((opp.scores or {}).get("fit", {}).get("reasons") or [])[:2]
    kind = (opp.analysis or {}).get("kind") or ""
    lines = [
        f"[{label_ru}] opp #{opp.id} · {opp.overall_score} баллов",
        opp.company_or_entity or "—",
        opp.title or "—",
        "",
        f"Что сделать: {action_how_ru(opp.next_action, opp.analysis or {})}",
    ]
    if kind == "freelance_order" and opp.source_url:
        lines.append(f"Ссылка: {opp.source_url}")
    if why:
        lines.append("Почему: " + "; ".join(why))
    if steps:
        lines.append("Шаги:")
        for s in steps:
            lines.append(f"• {s}")
    return {
        "opportunity_id": opp.id,
        "lead_id": None,
        "url": opp.source_url or "",
        "text": "\n".join(lines),
        "kind": "vertical",
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
    if (opp.analysis or {}).get("aggregator"):
        penalty += 2  # radar only — prefer HH/direct TG sources in brief
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
    clients: list[Any] | None = None,
    network: list[Any] | None = None,
    products: list[Any] | None = None,
    actions_n: int,
) -> str:
    clients = clients or []
    network = network or []
    products = products or []
    lines = [
        "📡 Бриф возможностей",
        "",
        "Как работать:",
        "• Вакансии: Открыть → отклик → «Откликнулся»",
        "• Клиент/Сеть/Продукт: кнопки Ок / Сделано / Мимо под карточкой",
        "• Чужие кейсы с сайта не упаковываем — только owned IP + новые идеи",
        "",
    ]

    if followups:
        lines.append("⚠ Тишина после отклика — сначала это:")
        for i, opp in enumerate(followups[:actions_n], 1):
            days = _days_since(opp.updated_at or opp.created_at)
            days_s = f"{days}д" if days is not None else "?"
            lead = opp.job_lead_id or opp.id
            lines.append(
                f"{i}) Follow-up #{lead} {opp.company_or_entity or '—'} (тишина {days_s})"
            )
        lines.append("")

    lines.append("📌 Вакансии (сегодня):")
    if not top:
        lines.append("• Сильных new нет — упор на клиент/сеть ниже")
    else:
        for i, opp in enumerate(top[:actions_n], 1):
            lead = opp.job_lead_id or opp.id
            lines.append(
                f"{i}) #{lead} {opp.company_or_entity or '—'} — "
                f"{action_how_ru(opp.next_action, opp.analysis or {})}"
            )
    lines.append("")

    if clients:
        lines.append("💼 Клиенты:")
        for opp in clients:
            lines.append(f"• opp #{opp.id} {opp.title[:70]}")
        lines.append("")
    if network:
        lines.append("🤝 Сеть:")
        for opp in network:
            lines.append(f"• opp #{opp.id} {opp.title[:70]}")
        lines.append("")
    if products:
        lines.append("📦 Продукт (новые идеи / своё IP):")
        for opp in products:
            kind = (opp.analysis or {}).get("kind") or ""
            tag = {"net_new": "новое", "owned_package": "своё", "ownership_gate": "уточнить IP"}.get(
                kind, kind
            )
            lines.append(f"• opp #{opp.id} [{tag}] {opp.title[:60]}")
        lines.append("")

    funnel = compute_funnel_snapshot()
    lines.extend(
        [
            "📊 Воронка (вакансии)",
            f"Новые: {funnel.get('new', 0)} · Избранное: {funnel.get('saved', 0)} · "
            f"Отклики: {funnel.get('applied', 0)} · Собесы: {funnel.get('interview', 0)}",
            "",
            "Карточки ↓",
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
        f"Что сделать: {action_how_ru(opp.next_action, opp.analysis or {})}",
    ]
    if why:
        lines.append("Почему в топе: " + "; ".join(why))
    hint = (opp.analysis or {}).get("apply_hint_ru") or ""
    if hint and hint not in "\n".join(lines):
        lines.append(f"Отклик: {hint}")
    if risks:
        lines.append("Риски: " + "; ".join(risks))
    elif (opp.analysis or {}).get("paywall") or (opp.analysis or {}).get("aggregator"):
        lines.append(
            "Риски: агрегатор/нет прямого контакта — не жми «отклик» в боте, ищи компанию"
        )

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
