"""Bug bounty semi-auto configuration."""

from __future__ import annotations

import os

from orchestrator.config import load_env_file

load_env_file(".env.bounty")

BOUNTY_ENABLED = os.environ.get("BOUNTY_ENABLED", "true").lower() in ("1", "true", "yes")
BOUNTY_AUTO_SUBMIT = os.environ.get("BOUNTY_AUTO_SUBMIT", "true").lower() in ("1", "true", "yes")
BOUNTY_MAX_PENDING = int(os.environ.get("BOUNTY_MAX_PENDING", "2"))
BOUNTY_RESEARCH_COOLDOWN_HOURS = int(os.environ.get("BOUNTY_RESEARCH_COOLDOWN_HOURS", "20"))
BOUNTY_PROGRAMS_PER_CYCLE = int(os.environ.get("BOUNTY_PROGRAMS_PER_CYCLE", "3"))
BOUNTY_REVIEW_ENABLED = os.environ.get("BOUNTY_REVIEW_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_MIN_QUALITY_SCORE = int(os.environ.get("BOUNTY_MIN_QUALITY_SCORE", "85"))
BOUNTY_RESEARCH_PHASES = os.environ.get("BOUNTY_RESEARCH_PHASES", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_SAVE_LEADS = os.environ.get("BOUNTY_SAVE_LEADS", "true").lower() in (
    "1",
    "true",
    "yes",
)
BOUNTY_SHOPIFY_FOCUS = os.environ.get("BOUNTY_SHOPIFY_FOCUS", "true").lower() in (
    "1",
    "true",
    "yes",
)

HACKERONE_API_USERNAME = os.environ.get("HACKERONE_API_USERNAME", "").strip()
# Some accounts use a separate token identifier from HackerOne settings (Basic auth username).
HACKERONE_API_IDENTIFIER = (
    os.environ.get("HACKERONE_API_IDENTIFIER", "").strip() or HACKERONE_API_USERNAME
)
HACKERONE_API_TOKEN = os.environ.get("HACKERONE_API_TOKEN", "").strip()

# Dev stores — domain required. Token: static shpat_* OR Dev Dashboard client credentials.
SHOPIFY_SHOP1_DOMAIN = os.environ.get("SHOPIFY_SHOP1_DOMAIN", "").strip()
SHOPIFY_SHOP1_ADMIN_TOKEN = os.environ.get("SHOPIFY_SHOP1_ADMIN_TOKEN", "").strip()
SHOPIFY_SHOP2_DOMAIN = os.environ.get("SHOPIFY_SHOP2_DOMAIN", "").strip()
SHOPIFY_SHOP2_ADMIN_TOKEN = os.environ.get("SHOPIFY_SHOP2_ADMIN_TOKEN", "").strip()

# Dev Dashboard app (dev.shopify.com) — exchange for 24h access token via client_credentials grant.
SHOPIFY_APP_CLIENT_ID = os.environ.get("SHOPIFY_APP_CLIENT_ID", "").strip()
SHOPIFY_APP_CLIENT_SECRET = os.environ.get("SHOPIFY_APP_CLIENT_SECRET", "").strip()


def shopify_test_stores_block() -> str:
    """Markdown for bounty prompts — never log tokens."""
    from bounty.shopify_auth import shop_has_auth

    lines: list[str] = []
    for i in (1, 2):
        domain = SHOPIFY_SHOP1_DOMAIN if i == 1 else SHOPIFY_SHOP2_DOMAIN
        if not domain:
            continue
        if shop_has_auth(i):
            auth = (
                "client_credentials (24h, auto-refresh)"
                if not (SHOPIFY_SHOP1_ADMIN_TOKEN if i == 1 else SHOPIFY_SHOP2_ADMIN_TOKEN)
                else "static env token"
            )
            lines.append(f"- Shop {i}: `{domain}` — Admin API **{auth}**")
        else:
            lines.append(f"- Shop {i}: `{domain}` — **no token** (add shpat_ or app client id/secret)")

    if not lines:
        return (
            "— нет dev stores в env. Добавь SHOPIFY_SHOP1_DOMAIN + "
            "(SHOPIFY_APP_CLIENT_ID/SECRET или SHOPIFY_SHOP1_ADMIN_TOKEN) в secrets/.env.bounty"
        )
    token_cmd = "cd /opt/personal-stack/agent && python3 -m bounty.shopify_token --shop 1"
    return "\n".join(
        [
            "Используй **только эти dev stores** (свои активы):",
            *lines,
            "",
            "Получить access token (Dev Dashboard — client id/secret, живёт ~24ч):",
            f"```\n{token_cmd}\n```",
            "",
            "Пример GraphQL (токен в переменную, не печатай в отчёте):",
            "```",
            'TOKEN=$(python3 -m bounty.shopify_token --shop 1)',
            'curl -sS "https://SHOP.myshopify.com/admin/api/2024-10/graphql.json" \\',
            '  -H "X-Shopify-Access-Token: $TOKEN" \\',
            '  -H "Content-Type: application/json" \\',
            '  -d \'{"query":"{ shop { name id } }"}\'',
            "```",
        ]
    )


KV_PROGRAM_INDEX = "bounty_program_index"
KV_LAST_RESEARCH = "bounty_last_research_ts"
