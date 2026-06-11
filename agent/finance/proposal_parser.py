"""Extract trade proposals from agent text output."""

from __future__ import annotations

import json
import re
from typing import Any

_REQUIRED_KEYS = frozenset({"market_id", "side", "size_usd"})
_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```",
    re.IGNORECASE,
)
_JSON_OBJECT_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)
_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*?\]", re.DOTALL)


def _normalize_proposal(raw: dict[str, Any]) -> dict[str, Any] | None:
    if not _REQUIRED_KEYS.issubset(raw.keys()):
        return None
    try:
        size = float(raw["size_usd"])
    except (TypeError, ValueError):
        return None
    if size <= 0:
        return None
    proposal: dict[str, Any] = {
        "market_id": str(raw["market_id"]),
        "side": str(raw.get("side", "buy")).lower(),
        "size_usd": size,
        "reason": str(raw.get("reason", "")),
    }
    for key in ("market_title", "question", "title"):
        if raw.get(key):
            proposal["market_title"] = str(raw[key])
            break
    if "open_positions" in raw:
        proposal["open_positions"] = int(raw["open_positions"])
    return proposal


def _collect_from_parsed(data: Any) -> list[dict[str, Any]]:
    items: list[Any]
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        return []

    proposals: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_proposal(item)
        if normalized:
            proposals.append(normalized)
    return proposals


def _try_parse_json(blob: str) -> list[dict[str, Any]]:
    try:
        return _collect_from_parsed(json.loads(blob))
    except json.JSONDecodeError:
        return []


def extract_trade_proposals(text: str) -> list[dict[str, Any]]:
    """Find JSON trade proposals containing market_id, side, and size_usd."""
    if not text or not text.strip():
        return []

    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    def add_batch(batch: list[dict[str, Any]]) -> None:
        for p in batch:
            key = json.dumps(p, sort_keys=True)
            if key not in seen:
                seen.add(key)
                results.append(p)

    add_batch(_try_parse_json(text.strip()))

    for match in _JSON_FENCE_RE.finditer(text):
        add_batch(_try_parse_json(match.group(1)))

    if '"market_id"' in text:
        for match in _JSON_ARRAY_RE.finditer(text):
            if '"market_id"' not in match.group(0):
                continue
            add_batch(_try_parse_json(match.group(0)))

        for match in _JSON_OBJECT_RE.finditer(text):
            if '"market_id"' not in match.group(0):
                continue
            add_batch(_try_parse_json(match.group(0)))

    return results
