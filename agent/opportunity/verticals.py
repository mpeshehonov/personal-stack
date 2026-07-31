"""CLIENT / NETWORK / PRODUCT opportunity generators (Jobs remains separate)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from opportunity.actions import decide_next_action
from opportunity.models import OpportunityStatus, OpportunityType
from opportunity.profile import load_profile, save_profile
from opportunity.repository import ensure_opportunity_schema
from orchestrator.state import get_conn

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scores(
    *,
    fit: int,
    income: int,
    growth: int,
    probability: int,
    strategic: int,
    urgency: int,
    why: list[str],
) -> dict[str, Any]:
    weights = {
        "fit": 0.20,
        "income": 0.25,
        "growth": 0.10,
        "probability": 0.15,
        "strategic": 0.15,
        "urgency": 0.15,
    }
    overall = int(
        round(
            fit * weights["fit"]
            + income * weights["income"]
            + growth * weights["growth"]
            + probability * weights["probability"]
            + strategic * weights["strategic"]
            + urgency * weights["urgency"]
        )
    )
    return {
        "fit": {"score": fit, "reasons": why[:2]},
        "income": {"score": income, "reasons": why[1:2] or why[:1]},
        "growth": {"score": growth, "reasons": []},
        "probability": {"score": probability, "reasons": []},
        "strategic": {"score": strategic, "reasons": why},
        "urgency": {"score": urgency, "reasons": []},
        "overall_score": overall,
        "weights": weights,
    }


def build_client_seeds(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """CLIENT opportunities: contract/retainer + explicit targets from profile."""
    out: list[dict[str, Any]] = []
    formats = [str(x).lower() for x in (profile.get("work_formats") or [])]
    contract_ok = any("contract" in f for f in formats)

    if contract_ok:
        out.append(
            {
                "key": "client:retainer-bridge",
                "type": OpportunityType.CLIENT.value,
                "title": "Контракт / retainer на 2–4 недели (мост к доходу)",
                "entity": "open market",
                "url": "",
                "why": [
                    "Вакансии могут молчать неделями — короткий контракт закрывает кассовый разрыв",
                    "Формат: React/Next модуль, доработки UI, касса/админка",
                ],
                "steps": [
                    "Написать 2 знакомым: «беру frontend на 2–4 недели, remote»",
                    "В Kwork/FL/TG-чатах — 1 объявление без демпинга",
                ],
                "fit": 75,
                "income": 88,
                "growth": 55,
                "probability": 60,
                "strategic": 80,
                "urgency": 90,
                "next": "WRITE_TO_CONTACT",
            }
        )

    for i, target in enumerate(profile.get("client_targets") or []):
        if not isinstance(target, dict):
            continue
        name = (target.get("name") or target.get("entity") or "").strip()
        if not name:
            continue
        key = target.get("key") or f"client:target:{i}:{name.lower().replace(' ', '-')[:40]}"
        out.append(
            {
                "key": key,
                "type": OpportunityType.CLIENT.value,
                "title": target.get("title") or f"Клиентский запрос: {name}",
                "entity": name,
                "url": target.get("url") or "",
                "why": target.get("why")
                or [f"Цель из профиля: {name}", target.get("notes") or "Написать оффер"],
                "steps": target.get("steps")
                or [
                    f"Короткое сообщение в {target.get('channel') or 'TG/email'}",
                    "Предложить конкретный объём (неделя / модуль), не «готов помочь»",
                ],
                "fit": int(target.get("fit") or 70),
                "income": int(target.get("income") or 80),
                "growth": int(target.get("growth") or 50),
                "probability": int(target.get("probability") or 55),
                "strategic": int(target.get("strategic") or 70),
                "urgency": int(target.get("urgency") or 75),
                "next": "WRITE_TO_CONTACT",
            }
        )

    if not out:
        out.append(
            {
                "key": "client:enable-contract",
                "type": OpportunityType.CLIENT.value,
                "title": "Включить контракты в профиль и набросать 3 цели",
                "entity": "profile setup",
                "url": "",
                "why": [
                    "CLIENT-вертикаль пустая: нет contract_ok и client_targets",
                ],
                "steps": [
                    "В opportunity_profile.json: work_formats += contract_ok",
                    "Добавь client_targets: [{name, channel, notes}]",
                ],
                "fit": 60,
                "income": 70,
                "growth": 40,
                "probability": 80,
                "strategic": 75,
                "urgency": 70,
                "next": "REVIEW",
            }
        )
    return out


def build_network_seeds(profile: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    contacts = profile.get("network_contacts") or []
    for i, c in enumerate(contacts):
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or "").strip()
        if not name:
            continue
        key = c.get("key") or f"network:{i}:{name.lower().replace(' ', '-')[:40]}"
        out.append(
            {
                "key": key,
                "type": OpportunityType.NETWORK.value,
                "title": c.get("title") or f"Написать: {name}",
                "entity": name,
                "url": c.get("url") or "",
                "why": [
                    c.get("relation") or "тёплый контакт",
                    c.get("notes") or "Попросить интро / вакансию / контракт",
                ],
                "steps": [
                    f"Канал: {c.get('channel') or 'TG/LinkedIn'}",
                    "Текст в 4 строки: ищу remote Senior FE / готов к короткому контракту",
                ],
                "fit": 70,
                "income": 65,
                "growth": 60,
                "probability": int(c.get("probability") or 70),
                "strategic": 85,
                "urgency": 80,
                "next": "WRITE_TO_CONTACT",
            }
        )

    # Standing weekly network action
    out.append(
        {
            "key": "network:weekly-one-human",
            "type": OpportunityType.NETWORK.value,
            "title": "1 сообщение человеку на этой неделе",
            "entity": "personal network",
            "url": "",
            "why": [
                "Доски дают тишину; один живой контакт часто сильнее 10 откликов",
            ],
            "steps": [
                "Выбери бывшего коллегу / однокурсника / чат",
                "Если списка нет — добавь network_contacts в opportunity_profile.json",
            ],
            "fit": 65,
            "income": 60,
            "growth": 55,
            "probability": 75 if contacts else 50,
            "strategic": 90,
            "urgency": 85,
            "next": "WRITE_TO_CONTACT",
        }
    )
    return out


def build_product_seeds(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """PRODUCT: owned resell assets only + net-new theses (never employer case studies)."""
    out: list[dict[str, Any]] = []
    blocked = {
        str(x).lower()
        for x in (profile.get("product_ideas_blocked") or [])
    }
    # Hard blocks for known non-owned employer work names
    blocked |= {
        "x5",
        "citilink",
        "sendonate",
        "preeglos",
        "bi.zone",
        "nlmk",
        "potalonu",
        "seats.io",
        "rostelecom",
        "sbertech",
        "zenit",
        "baucenter",
        "maximaster",
        "akvaprom",
    }

    for asset in profile.get("owned_product_assets") or []:
        if not isinstance(asset, dict):
            continue
        if not asset.get("can_resell"):
            continue
        key_name = str(asset.get("key") or asset.get("title") or "").lower()
        if any(b in key_name for b in blocked if len(b) >= 3):
            continue
        title = asset.get("title") or asset.get("key") or "Owned product"
        key = f"product:owned:{asset.get('key') or title.lower().replace(' ', '-')[:40]}"
        out.append(
            {
                "key": key,
                "type": OpportunityType.PRODUCT.value,
                "title": f"Упаковать и предложить: {title}",
                "entity": title,
                "url": asset.get("url") or "",
                "why": [
                    "Явно помечено can_resell=true в профиле (не кейс работодателя)",
                    asset.get("notes") or "Собрать one-pager + цена + канал продаж",
                ],
                "steps": asset.get("steps")
                or [
                    "1 страница: проблема / для кого / цена / срок",
                    "Написать 3 потенциальным покупателям",
                ],
                "fit": 80,
                "income": 85,
                "growth": 70,
                "probability": 55,
                "strategic": 88,
                "urgency": 70,
                "next": "REVIEW",
                "kind": "owned_package",
            }
        )

    # Net-new product opportunities (not claiming past employer IP)
    net_new = [
        {
            "key": "product:net-new:tablet-pos-lite",
            "title": "Новый продукт: лёгкая касса на планшете (Expo) для мелкой розницы",
            "entity": "net-new POS",
            "why": [
                "Стек RN/Expo уже в навыках; рынок мелкой розницы платит за простоту, не за 1С",
                "Это не SmartFish IP — новая упрощённая версия под другой сегмент",
            ],
            "steps": [
                "Валидация: 5 разговоров с владельцами точек (не код)",
                "MVP: смена + корзина + чек-заглушка, без полного ERP",
            ],
            "fit": 78,
            "income": 75,
            "growth": 90,
            "probability": 40,
            "strategic": 92,
            "urgency": 60,
        },
        {
            "key": "product:net-new:seatmap-widget-saas",
            "title": "Новый продукт: встраиваемый виджет схемы зала (SaaS lite)",
            "entity": "net-new seatmap",
            "why": [
                "Навык Canvas/схем залов есть; seats.io дорогой — ниша малых организаторов",
                "Не перепродавать PREEGLOS/клиентский код — новый white-label с нуля",
            ],
            "steps": [
                "Landing + waitlist (без полной реализации редактора)",
                "Спросить 3 ивент-организаторов: платили бы X₽/мес?",
            ],
            "fit": 72,
            "income": 70,
            "growth": 88,
            "probability": 35,
            "strategic": 90,
            "urgency": 55,
        },
        {
            "key": "product:net-new:fe-contract-kit",
            "title": "Новый продукт: шаблон «frontend module delivery» для студий",
            "entity": "net-new kit",
            "why": [
                "Упаковать процесс (Vite/Next, OpenAPI client, CI) как продукт/консалтинг-пакет",
                "Не код X5/Citilink — методология + boilerplate своего",
            ],
            "steps": [
                "Описать пакет: discovery → API → UI → CI за фикс. цену",
                "Продать 1 раз знакомой студии/аутстаффу",
            ],
            "fit": 70,
            "income": 72,
            "growth": 75,
            "probability": 50,
            "strategic": 80,
            "urgency": 65,
        },
        {
            "key": "product:net-new:tg-ops-bot-kit",
            "title": "Новый продукт: self-hosted набор TG-ботов для малого бизнеса",
            "entity": "net-new tg ops",
            "why": [
                "Опыт ботов/Mini App есть; малый бизнес платит за отчёты, заказы, CRM-lite без Bitrix",
                "Не форк ZodiacLab/SmartFish — новый шаблон под другую вертикаль (кафе / сервис / студия)",
            ],
            "steps": [
                "Выбрать 1 нишу и 3 must-have сценария (заказ / напоминание / отчёт)",
                "Landing + демо-бот; 5 разговоров с владельцами до кода",
            ],
            "fit": 76,
            "income": 78,
            "growth": 85,
            "probability": 45,
            "strategic": 88,
            "urgency": 70,
        },
        {
            "key": "product:net-new:opportunity-os-saas",
            "title": "Новый продукт: Opportunity OS для джобханта (личный агент)",
            "entity": "net-new opportunity os",
            "why": [
                "Уже строится в personal-stack — можно вынести как paid self-hosted / hosted для RF remote",
                "Дифференциатор: multi-vertical (jobs+clients+network), не ещё один HH-агрегатор",
            ],
            "steps": [
                "Описать MVP для чужого резюме (1 профиль + /brief + 2 источника)",
                "Спросить 3 знакомых джобхантеров: платили бы за self-hosted?",
            ],
            "fit": 85,
            "income": 65,
            "growth": 95,
            "probability": 35,
            "strategic": 95,
            "urgency": 55,
        },
        {
            "key": "product:net-new:creator-alerts-lite",
            "title": "Новый продукт: лёгкие алерты для стримеров (без донат-платформы)",
            "entity": "net-new creator alerts",
            "why": [
                "Навык OBS/WebSocket/Mini App есть; ниша — алерты из своих источников (Twitch/YouTube/касса), не клон sendonate",
                "Не трогать код/бренд sendonate — другой ICP и другой платежный контур",
            ],
            "steps": [
                "1 страница: «алерты из X без смены донат-сервиса»",
                "Валидация с 5 стримерами, которые уже на другой платформе",
            ],
            "fit": 68,
            "income": 60,
            "growth": 80,
            "probability": 30,
            "strategic": 75,
            "urgency": 50,
        },
    ]
    for idea in net_new:
        blob = (idea["title"] + " " + idea["entity"]).lower()
        if any(b in blob for b in blocked if len(b) >= 4):
            continue
        out.append(
            {
                **idea,
                "type": OpportunityType.PRODUCT.value,
                "url": "",
                "next": "CONSIDER_SWITCH",
                "kind": "net_new",
            }
        )

    if not profile.get("owned_product_assets"):
        out.insert(
            0,
            {
                "key": "product:confirm-owned-assets",
                "type": OpportunityType.PRODUCT.value,
                "title": "Подтвердить, что можно упаковывать (owned IP)",
                "entity": "profile gate",
                "url": "",
                "why": [
                    "Кейсы работодателей с сайта нельзя перепродавать",
                    "Нужен список owned_product_assets с can_resell=true",
                ],
                "steps": [
                    "Ответь агенту: SmartFish KKM / SmartPrice / ZodiacLab / другое — что твоё?",
                    "Запишем в opportunity_profile.json только разрешённое",
                ],
                "fit": 50,
                "income": 40,
                "growth": 50,
                "probability": 90,
                "strategic": 95,
                "urgency": 80,
                "next": "REVIEW",
                "kind": "ownership_gate",
            },
        )
    return out


def upsert_seed(seed: dict[str, Any]) -> int:
    ensure_opportunity_schema()
    now = _utcnow()
    why = list(seed.get("why") or [])
    scores = _scores(
        fit=int(seed.get("fit") or 60),
        income=int(seed.get("income") or 60),
        growth=int(seed.get("growth") or 50),
        probability=int(seed.get("probability") or 50),
        strategic=int(seed.get("strategic") or 60),
        urgency=int(seed.get("urgency") or 60),
        why=why,
    )
    analysis = {
        "kind": seed.get("kind") or seed.get("type", "").lower(),
        "actionable": True,
        "paywall": False,
        "steps": seed.get("steps") or [],
        "vertical": seed.get("type"),
    }
    next_action = seed.get("next") or "REVIEW"
    priority = "HIGH" if scores["overall_score"] >= 80 else "MEDIUM"
    # Respect decide_next_action for status new when next not forced
    if next_action not in (
        "WRITE_TO_CONTACT",
        "CONSIDER_SWITCH",
        "REVIEW",
        "APPLY",
        "FOLLOW_UP",
    ):
        next_action, priority = decide_next_action(
            status=OpportunityStatus.NEW,
            scores=scores,
            analysis=analysis,
        )

    payload = json.dumps(seed, ensure_ascii=False)
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, status FROM opportunities WHERE source = ?",
            (seed["key"],),
        ).fetchone()
        # Don't revive archived/skipped by generator
        if existing and existing["status"] in (
            "skipped",
            "archived",
            "rejected",
            "hired",
        ):
            return int(existing["id"])

        if existing:
            conn.execute(
                """
                UPDATE opportunities SET
                    type=?, title=?, company_or_entity=?, source_url=?,
                    updated_at=?, raw_payload=?, normalized_payload=?,
                    scores_json=?, analysis_json=?, next_action=?,
                    next_action_priority=?, overall_score=?
                WHERE id=?
                """,
                (
                    seed["type"],
                    seed["title"],
                    seed.get("entity") or "",
                    seed.get("url") or "",
                    now,
                    payload,
                    payload,
                    json.dumps(scores, ensure_ascii=False),
                    json.dumps(analysis, ensure_ascii=False),
                    next_action,
                    priority,
                    int(scores["overall_score"]),
                    int(existing["id"]),
                ),
            )
            return int(existing["id"])

        cur = conn.execute(
            """
            INSERT INTO opportunities(
                type, title, company_or_entity, source, source_url, status,
                created_at, updated_at, raw_payload, normalized_payload,
                scores_json, analysis_json, next_action, next_action_priority,
                overall_score, job_lead_id
            ) VALUES(?, ?, ?, ?, ?, 'new', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                seed["type"],
                seed["title"],
                seed.get("entity") or "",
                seed["key"],
                seed.get("url") or "",
                now,
                now,
                payload,
                payload,
                json.dumps(scores, ensure_ascii=False),
                json.dumps(analysis, ensure_ascii=False),
                next_action,
                priority,
                int(scores["overall_score"]),
            ),
        )
        return int(cur.lastrowid)


def ensure_vertical_opportunities(profile: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = profile or load_profile()
    # Ensure new profile keys exist on disk
    dirty = False
    for key, default in (
        ("client_targets", []),
        ("network_contacts", []),
        ("owned_product_assets", []),
        ("product_ideas_blocked", ["sendonate", "preeglos", "x5", "citilink", "potalonu"]),
    ):
        if key not in profile:
            profile[key] = default
            dirty = True
    if dirty:
        save_profile(profile)

    seeds: list[dict[str, Any]] = []
    seeds.extend(build_client_seeds(profile))
    seeds.extend(build_network_seeds(profile))
    seeds.extend(build_product_seeds(profile))

    by_type: dict[str, int] = {}
    titles: list[str] = []
    for seed in seeds:
        upsert_seed(seed)
        by_type[seed["type"]] = by_type.get(seed["type"], 0) + 1
        titles.append(seed["title"])

    logger.info("Vertical opportunities upserted: %s", by_type)
    return {"by_type": by_type, "titles": titles[:12], "count": len(seeds)}
