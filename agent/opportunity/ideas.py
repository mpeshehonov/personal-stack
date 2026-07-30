"""Strategic non-vacancy ideas: specialization switches, niches, income stabilizers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from opportunity.actions import decide_next_action
from opportunity.models import OpportunityStatus, OpportunityType
from opportunity.profile import load_profile
from opportunity.repository import ensure_opportunity_schema
from orchestrator.state import get_conn


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_strategic_ideas(profile: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Deterministic idea cards from profile gaps — not scraped jobs."""
    p = profile or load_profile()
    interests = p.get("strategic_interests") or []
    adjacent = p.get("adjacent_roles") or []
    ideas: list[dict[str, Any]] = []

    ideas.append(
        {
            "key": "idea:stabilize-income-multi-channel",
            "title": "Не ставь всё только на отклики — часто тишина",
            "entity": "personal strategy",
            "why": [
                "Если только жать «отклик» на досках, недели уходят в пустоту",
            ],
            "steps": [
                "2–3 нормальных отклика по карточкам ниже (и жми «Откликнулся»)",
                "1 сильную вакансию без контактов — найди компанию в LinkedIn/HH и напиши туда",
                "1 сообщение человеку (бывший коллега / чат): «ищу remote Senior FE»",
            ],
            "next": "REVIEW",
            "overall": 88,
            "strategic": 95,
        }
    )

    if any("react native" in str(x).lower() or "expo" in str(x).lower() for x in interests + adjacent):
        ideas.append(
            {
                "key": "idea:rn-expo-switch",
                "title": "Смежный трек: React Native / Expo (не полный свитч)",
                "entity": "specialization",
                "why": [
                    "В резюме уже есть RN/Expo + кейс SmartFish KKM",
                ],
                "steps": [
                    "На этой неделе откликнуться на 1 remote RN/Expo роль (не junior)",
                    "В сопроводительном писать: основной трек web FE, RN — смежный опыт",
                ],
                "next": "CONSIDER_SWITCH",
                "overall": 82,
                "strategic": 90,
            }
        )

    if any("seat" in str(x).lower() or "canvas" in str(x).lower() or "ticket" in str(x).lower() for x in interests):
        ideas.append(
            {
                "key": "idea:seatmap-niche",
                "title": "Ниша: редакторы схем залов / seat maps",
                "entity": "product niche",
                "why": [
                    "PREEGLOS: Canvas editor + embed widget — редкий сигнал",
                    "Можно предлагать компаниям event/ticketing как contractor",
                ],
                "next": "RESEARCH_COMPANY",
                "overall": 78,
                "strategic": 88,
            }
        )

    if any("web3" in str(x).lower() or "ton" in str(x).lower() for x in interests):
        ideas.append(
            {
                "key": "idea:web3-fe",
                "title": "Точечно: Web3/TON frontend (не ставка всей карьеры)",
                "entity": "adjacent market",
                "why": [
                    "Стек в резюме есть; рынок узкий, но вилки часто выше",
                    "Фильтровать scam/junior bounty noise",
                ],
                "next": "CONSIDER_SWITCH",
                "overall": 70,
                "strategic": 75,
            }
        )

    ideas.append(
        {
            "key": "idea:contract-bridge",
            "title": "Подработка/контракт, пока нет оффера",
            "entity": "work format",
            "why": [
                "Full-time может молчать неделями — короткий контракт закрывает кассовый разрыв",
            ],
            "steps": [
                "Написать 1–2 знакомым: готов взять frontend на 2–4 недели",
                "Не снимать основной поиск Senior FE",
            ],
            "next": "REVIEW",
            "overall": 80,
            "strategic": 85,
        }
    )
    return ideas


def ensure_strategic_ideas() -> dict[str, Any]:
    ensure_opportunity_schema()
    ideas = build_strategic_ideas()
    upserted = 0
    titles: list[str] = []
    now = _utcnow()
    with get_conn() as conn:
        for idea in ideas:
            key = idea["key"]
            existing = conn.execute(
                """
                SELECT id FROM opportunities
                WHERE type = ? AND source = ?
                """,
                (OpportunityType.OTHER.value, key),
            ).fetchone()
            scores = {
                "fit": {"score": 70, "reasons": idea["why"][:2]},
                "income": {"score": 75, "reasons": ["стабилизация дохода"]},
                "growth": {"score": 80, "reasons": idea["why"][1:2] or ["рост опций"]},
                "probability": {"score": 55, "reasons": ["требует ручного действия"]},
                "strategic": {"score": idea.get("strategic", 80), "reasons": idea["why"]},
                "urgency": {"score": 70, "reasons": ["RED / ASAP context"]},
                "overall_score": idea["overall"],
                "weights": {},
            }
            analysis = {"kind": "strategic_idea", "actionable": True, "paywall": False}
            next_action, priority = decide_next_action(
                status=OpportunityStatus.NEW,
                scores=scores,
                analysis=analysis,
            )
            if idea.get("next") == "CONSIDER_SWITCH":
                next_action = "CONSIDER_SWITCH"
            payload = json.dumps(idea, ensure_ascii=False)
            if existing:
                conn.execute(
                    """
                    UPDATE opportunities SET
                        title=?, company_or_entity=?, updated_at=?,
                        scores_json=?, analysis_json=?, next_action=?,
                        next_action_priority=?, overall_score=?,
                        normalized_payload=?, status='new'
                    WHERE id=?
                    """,
                    (
                        idea["title"],
                        idea["entity"],
                        now,
                        json.dumps(scores, ensure_ascii=False),
                        json.dumps(analysis, ensure_ascii=False),
                        next_action,
                        priority,
                        int(idea["overall"]),
                        payload,
                        int(existing["id"]),
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO opportunities(
                        type, title, company_or_entity, source, source_url, status,
                        created_at, updated_at, raw_payload, normalized_payload,
                        scores_json, analysis_json, next_action, next_action_priority,
                        overall_score, job_lead_id
                    ) VALUES(?, ?, ?, ?, '', 'new', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                    """,
                    (
                        OpportunityType.OTHER.value,
                        idea["title"],
                        idea["entity"],
                        key,
                        now,
                        now,
                        payload,
                        payload,
                        json.dumps(scores, ensure_ascii=False),
                        json.dumps(analysis, ensure_ascii=False),
                        next_action,
                        priority,
                        int(idea["overall"]),
                    ),
                )
            upserted += 1
            titles.append(idea["title"])
    return {"upserted": upserted, "titles": titles}
