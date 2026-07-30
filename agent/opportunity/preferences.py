"""Explainable preference model — slow weight/feature updates from feedback."""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from opportunity.profile import load_profile, save_profile
from opportunity.repository import list_opportunity_feedback, list_opportunities

logger = logging.getLogger(__name__)

# Cap how far preferences can move per rebuild
MAX_WEIGHT_DELTA = 0.05
MAX_FEATURE_BOOST = 8.0
MIN_SAMPLES = 5


POSITIVE = frozenset({"LIKE", "SAVE", "APPLY", "INTERVIEW", "OFFER", "HIRED"})
NEGATIVE = frozenset({"DISLIKE", "SKIP", "NOT_RELEVANT", "REJECTED"})


def _feature_keys(opp: Any) -> list[str]:
    keys = []
    src = (opp.source or "").split(":")[0]
    if src:
        keys.append(f"source:{src}")
    title = (opp.title or "").lower()
    for token in ("senior", "lead", "react", "next", "remote", "vue", "angular", "mobile"):
        if token in title:
            keys.append(f"title:{token}")
    company = (opp.company_or_entity or "").strip().lower()
    if company:
        keys.append(f"company:{company[:40]}")
    return keys


def rebuild_preferences(*, dry_run: bool = False) -> dict[str, Any]:
    """
    Analyze opportunity feedback vs features.
    Does nothing meaningful until MIN_SAMPLES feedback events.
    """
    feedback = list_opportunity_feedback(limit=500)
    if len(feedback) < MIN_SAMPLES:
        return {
            "updated": False,
            "reason": f"need ≥{MIN_SAMPLES} feedback events, have {len(feedback)}",
            "samples": len(feedback),
        }

    # Map opp_id → latest action
    latest: dict[int, str] = {}
    for row in feedback:
        oid = int(row["opportunity_id"])
        if oid not in latest:
            latest[oid] = row["action"]

    pos_features: Counter[str] = Counter()
    neg_features: Counter[str] = Counter()
    opps = {o.id: o for o in list_opportunities(status=None, limit=500, min_overall=0)}

    for oid, action in latest.items():
        opp = opps.get(oid)
        if opp is None:
            continue
        feats = _feature_keys(opp)
        if action in POSITIVE:
            pos_features.update(feats)
        elif action in NEGATIVE:
            neg_features.update(feats)

    feature_boosts: dict[str, float] = {}
    explanations: list[str] = []
    all_keys = set(pos_features) | set(neg_features)
    for key in all_keys:
        p = pos_features[key]
        n = neg_features[key]
        total = p + n
        if total < 3:
            continue
        rate = (p - n) / total
        boost = max(-MAX_FEATURE_BOOST, min(MAX_FEATURE_BOOST, rate * MAX_FEATURE_BOOST))
        if abs(boost) < 1.5:
            continue
        # Store without source: prefix for title matching in scorer (simple contains)
        label = key.split(":", 1)[-1]
        feature_boosts[label] = round(boost, 2)
        explanations.append(
            f"{label}: pos={p} neg={n} → boost {boost:+.1f}"
        )

    # Gentle weight tilt: if APPLY/INTERVIEW rare vs LIKE, boost probability weight slightly
    actions = Counter(latest.values())
    weight_deltas: dict[str, float] = {}
    appliedish = actions.get("APPLY", 0) + actions.get("INTERVIEW", 0)
    liked = actions.get("LIKE", 0) + actions.get("SAVE", 0)
    if liked >= 3 and appliedish == 0:
        weight_deltas["probability"] = MAX_WEIGHT_DELTA
        explanations.append(
            "много LIKE без APPLY → +probability weight "
            f"(actionability важнее), delta={MAX_WEIGHT_DELTA}"
        )
    if actions.get("NOT_RELEVANT", 0) + actions.get("DISLIKE", 0) >= liked + 3:
        weight_deltas["fit"] = MAX_WEIGHT_DELTA
        explanations.append("много негатива → чуть усиливаем fit filter")

    result = {
        "updated": True,
        "samples": len(feedback),
        "feature_boosts": feature_boosts,
        "weight_deltas": weight_deltas,
        "explanations": explanations,
    }
    if dry_run:
        result["updated"] = False
        result["dry_run"] = True
        return result

    profile = load_profile()
    profile["preference_adjustments"] = {
        "feature_boosts": feature_boosts,
        "weight_deltas": weight_deltas,
        "last_rebuild_samples": len(feedback),
        "explanations": explanations[:20],
    }
    save_profile(profile)
    logger.info("Preferences rebuilt: %s", explanations[:5])
    return result


def format_preference_explain() -> str:
    profile = load_profile()
    adj = profile.get("preference_adjustments") or {}
    if not adj:
        return "Preference model ещё пустой (мало feedback)."
    lines = ["Preference model:", ""]
    for line in adj.get("explanations") or []:
        lines.append(f"• {line}")
    if adj.get("feature_boosts"):
        lines.append("")
        lines.append("Feature boosts: " + ", ".join(
            f"{k}={v:+.1f}" for k, v in adj["feature_boosts"].items()
        ))
    if adj.get("weight_deltas"):
        lines.append(
            "Weight deltas: "
            + ", ".join(f"{k}={v:+.3f}" for k, v in adj["weight_deltas"].items())
        )
    return "\n".join(lines)
