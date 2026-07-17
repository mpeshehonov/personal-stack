"""Weekly bounty program rotation suggestions — BB-06."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from bounty.config import BOUNTY_SHOPIFY_FOCUS, KV_PROGRAM_INDEX
from bounty.payout_rail import PLATFORM_RAILS
from bounty.programs import WEB_JS_PROGRAMS, BountyProgram, program_by_index
from orchestrator.state import (
    get_conn,
    get_last_program_suggestion,
    kv_get,
    set_last_program_suggestion,
)

DEPRIORITIZED_HANDLES = frozenset({"ikea", "mozilla"})
CRYPTO_PRIORITY_HANDLES = frozenset({"0x", "edgex", "backpack", "gmx", "1inch-web"})


@dataclass(frozen=True)
class ProgramSuggestion:
    focus: tuple[str, ...]
    deprioritize: tuple[str, ...]
    rotate_next: str
    crypto_next: str
    program_index: int
    rationale: str
    is_fresh: bool

    def to_markdown(self) -> str:
        focus = ", ".join(self.focus) or "—"
        deprio = ", ".join(self.deprioritize) or "—"
        fresh = "новая" if self.is_fresh else "кэш (<7 дней с прошлой)"
        return (
            f"**Weekly program suggestion** ({fresh}):\n"
            f"- **Focus:** {focus}\n"
            f"- **Deprioritize:** {deprio}\n"
            f"- **Scanner index:** {self.program_index} → {self.rotate_next}\n"
            f"- **Crypto rotation (when SHOPIFY_FOCUS off):** {self.crypto_next}\n"
            f"- **Rationale:** {self.rationale}"
        )


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _draft_stats_by_handle() -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT status, meta_json, title FROM bounty_drafts"
        ).fetchall()
    for row in rows:
        meta = json.loads(row["meta_json"] or "{}")
        handle = (
            meta.get("team_handle") or meta.get("program") or ""
        ).lower()
        title = row["title"] or ""
        if not handle and ("GHSA" in title or "Review GHSA" in title):
            handle = "_ghsa_spam"
        if handle not in stats:
            stats[handle] = {"pending": 0, "rejected": 0, "accepted": 0}
        status = row["status"]
        if status in stats[handle]:
            stats[handle][status] += 1
    return stats


def _score_program(prog: BountyProgram, stats: dict[str, dict[str, int]]) -> int:
    rail = PLATFORM_RAILS.get(prog.platform, "unknown")
    score = 0
    if rail == "crypto":
        score += 30
    elif rail == "bank":
        score -= 20
    if prog.team_handle in CRYPTO_PRIORITY_HANDLES:
        score += 15
    if prog.team_handle in DEPRIORITIZED_HANDLES:
        score -= 25
    s = stats.get(prog.team_handle.lower(), {})
    if s.get("rejected", 0) >= 3 and s.get("accepted", 0) == 0:
        score -= 10
    if prog.team_handle == "shopify":
        score += 20
    return score


def build_weekly_suggestion(*, force: bool = False) -> ProgramSuggestion:
    last = _parse_ts(get_last_program_suggestion())
    is_fresh = force or not last or (_utcnow() - last) >= timedelta(days=7)

    stats = _draft_stats_by_handle()
    scored = sorted(
        ((_score_program(p, stats), p) for p in WEB_JS_PROGRAMS),
        key=lambda item: -item[0],
    )

    focus: list[str] = []
    for _, prog in scored:
        if prog.team_handle in DEPRIORITIZED_HANDLES:
            continue
        if len(focus) >= 4:
            break
        focus.append(f"{prog.name} ({prog.platform})")

    deprioritize: list[str] = []
    for _, prog in scored:
        if prog.team_handle in DEPRIORITIZED_HANDLES:
            deprioritize.append(f"{prog.name} — bank payout, poor RU fit")
        elif PLATFORM_RAILS.get(prog.platform) == "bank":
            deprioritize.append(f"{prog.name} — {prog.platform} bank rail")

    ghsa = stats.get("_ghsa_spam", {})
    if ghsa.get("rejected", 0) >= 5:
        deprioritize.append(
            f"GHSA/CVE advisory mining — {ghsa['rejected']} rejected, zero payout path"
        )

    try:
        program_index = int(kv_get(KV_PROGRAM_INDEX, "0") or "0")
    except ValueError:
        program_index = 0

    rotate_next = (
        "Shopify (BOUNTY_SHOPIFY_FOCUS=true)"
        if BOUNTY_SHOPIFY_FOCUS
        else program_by_index(program_index).name
    )

    crypto_next = next(
        (
            p.name
            for _, p in scored
            if PLATFORM_RAILS.get(p.platform) == "crypto"
            and p.team_handle not in DEPRIORITIZED_HANDLES
        ),
        "0x / Matcha",
    )

    rejected_total = sum(s.get("rejected", 0) for s in stats.values())
    rationale = (
        f"{rejected_total} rejected drafts; crypto payout (Immunefi/HackenProof) "
        f"prioritized for RU wallet path; rotate away from bank-only programs."
    )

    if is_fresh:
        set_last_program_suggestion()

    return ProgramSuggestion(
        focus=tuple(focus),
        deprioritize=tuple(deprioritize),
        rotate_next=rotate_next,
        crypto_next=crypto_next,
        program_index=program_index,
        rationale=rationale,
        is_fresh=is_fresh,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly bounty program suggestion (BB-06)")
    parser.add_argument("--force", action="store_true", help="Ignore 7-day cadence")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    suggestion = build_weekly_suggestion(force=args.force)
    if args.json:
        print(
            json.dumps(
                {
                    "focus": list(suggestion.focus),
                    "deprioritize": list(suggestion.deprioritize),
                    "rotate_next": suggestion.rotate_next,
                    "crypto_next": suggestion.crypto_next,
                    "program_index": suggestion.program_index,
                    "rationale": suggestion.rationale,
                    "is_fresh": suggestion.is_fresh,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(suggestion.to_markdown())


if __name__ == "__main__":
    main()
