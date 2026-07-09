"""Payout rail resolution for bounty drafts — BB-07."""

from __future__ import annotations

import argparse
import json
from typing import Literal

from orchestrator.state import get_conn, get_bounty_draft_meta, update_bounty_draft_meta

PayoutRail = Literal["crypto", "bank", "unknown"]

PLATFORM_RAILS: dict[str, PayoutRail] = {
    "immunefi": "crypto",
    "hackenproof": "crypto",
    "hackerone": "unknown",
    "bugcrowd": "bank",
    "intigriti": "bank",
}

VALID_PAYOUT_RAILS = frozenset(PLATFORM_RAILS.values())


def resolve_payout_rail(platform: str, *, team_handle: str = "") -> PayoutRail:
    """Map platform (and optional handle) to payout rail for draft meta."""
    _ = team_handle  # reserved for per-program overrides (e.g. H1 crypto toggle)
    return PLATFORM_RAILS.get(platform.strip().lower(), "unknown")


def tag_lead_meta(meta: dict, platform: str, *, team_handle: str = "") -> dict:
    """Ensure lead draft meta includes payout_rail."""
    out = dict(meta)
    out["payout_rail"] = resolve_payout_rail(platform, team_handle=team_handle)
    return out


def backfill_lead_payout_rails(*, dry_run: bool = False) -> list[tuple[int, str]]:
    """Add payout_rail to existing [Lead] drafts missing the field."""
    updated: list[tuple[int, str]] = []
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, title, meta_json FROM bounty_drafts
            WHERE title LIKE '[Lead]%' OR json_extract(meta_json, '$.kind') = 'lead'
            """
        ).fetchall()
    for row in rows:
        draft_id = int(row["id"])
        meta = json.loads(row["meta_json"] or "{}")
        if meta.get("payout_rail") in VALID_PAYOUT_RAILS:
            continue
        platform = str(meta.get("platform", ""))
        team_handle = str(meta.get("team_handle", ""))
        rail = resolve_payout_rail(platform, team_handle=team_handle)
        if not dry_run:
            meta["payout_rail"] = rail
            update_bounty_draft_meta(draft_id, meta)
        updated.append((draft_id, rail))
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill payout_rail on [Lead] drafts (BB-07)")
    parser.add_argument("--dry-run", action="store_true", help="List changes without writing")
    args = parser.parse_args()
    updated = backfill_lead_payout_rails(dry_run=args.dry_run)
    if not updated:
        print("No lead drafts need payout_rail backfill.")
        return
    action = "would update" if args.dry_run else "updated"
    for draft_id, rail in updated:
        print(f"#{draft_id}: {action} payout_rail={rail}")


if __name__ == "__main__":
    main()
