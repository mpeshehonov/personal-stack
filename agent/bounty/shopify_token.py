"""Print Shopify Admin API token for curl / bounty hunt (Dev Dashboard client credentials)."""

from __future__ import annotations

import argparse
import sys

from bounty.shopify_auth import get_admin_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Get Shopify Admin API access token")
    parser.add_argument("--shop", type=int, default=1, choices=(1, 2))
    args = parser.parse_args()
    try:
        print(get_admin_token(args.shop))
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
