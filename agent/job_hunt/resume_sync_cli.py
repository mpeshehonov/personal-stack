"""CLI entry for resume sync — auth check, plan, push."""

from __future__ import annotations

import argparse

from job_hunt.resume_sync import apply_sync, format_auth_markdown, format_sync_plan_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Job hunt resume sync")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("auth", help="Check Habr/LinkedIn credentials")
    sub.add_parser("plan", help="Show diff vs last sync")
    sub.add_parser("hh-digest", help="HH manual paste blocks (API closed)")
    push = sub.add_parser("push", help="Apply sync")
    push.add_argument(
        "platform",
        choices=["hh", "habr", "linkedin", "all"],
        nargs="?",
        default="habr",
    )

    args = parser.parse_args()

    if args.cmd == "auth":
        print(format_auth_markdown())
        return 0

    if args.cmd == "plan":
        print(format_sync_plan_markdown())
        return 0

    if args.cmd == "hh-digest":
        from job_hunt.hh_digest import format_hh_digest_markdown

        print(format_hh_digest_markdown())
        return 0

    if args.cmd == "push":
        result = apply_sync(args.platform)
        print(f"OK={result.get('ok')}")
        for name, detail in (result.get("platforms") or {}).items():
            print(f"  {name}: {detail.get('message', detail)}")
        return 0 if result.get("ok") else 1

    return 1
