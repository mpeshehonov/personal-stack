---
name: bounty-shopify
description: Authenticated Shopify bug bounty on dev stores — Dev Dashboard client credentials, GraphQL IDOR, staff RBAC, checkout logic. Use when team_handle is shopify.
---

# Bounty — Shopify (authenticated)

Playbook: `agent/tasks/bounty_shopify_playbook.md`.

## Auth model (2026)

Apps in **dev.shopify.com** no longer show a copy-paste `shpat_` in the UI. You get **Client ID + Client secret** and exchange them for a **24-hour** Admin API access token ([docs](https://shopify.dev/docs/apps/build/dev-dashboard/get-api-access-tokens)).

`secrets/.env.bounty`:

```bash
SHOPIFY_SHOP1_DOMAIN=test-store-....myshopify.com
SHOPIFY_APP_CLIENT_ID=...
SHOPIFY_APP_CLIENT_SECRET=shpss_...
```

Optional: static `SHOPIFY_SHOP1_ADMIN_TOKEN=shpat_...` if you still have a legacy custom app.

## Setup checklist

1. Partner + dev store (bug bounty signup, `@wearehackerone.com` alias)
2. **dev.shopify.com** → create app → configure **Admin API scopes** on app version
3. **Install app on the dev store** (Dev Dashboard → app → install / test on store)
4. Env on server + verify:

```bash
cd /opt/personal-stack/agent
python3 -m bounty.shopify_token --shop 1
```

Should print an access token (not an error). Orchestrator caches it in `secrets/.shopify_token_cache.json`.

Manual exchange:

```bash
curl -X POST "https://SHOP.myshopify.com/admin/oauth/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=CLIENT_ID" \
  -d "client_secret=CLIENT_SECRET"
```

**Common error:** `shop_not_permitted` — app not installed on this store, or app/store in different orgs.

## Hunt priorities

| Priority | Technique |
|----------|-----------|
| 1 | GraphQL IDOR across shop contexts |
| 2 | Staff RBAC escalation |
| 3 | Discount / checkout logic on your store |
| 4 | Webhook SSRF |
| 5 | OAuth redirect_uri on your Dev Dashboard app |

## API usage

```bash
TOKEN=$(python3 -m bounty.shopify_token --shop 1)
curl -sS "https://SHOP.myshopify.com/admin/api/2024-10/shop.json" \
  -H "X-Shopify-Access-Token: $TOKEN"
```

Redact tokens in bounty drafts.

## Pipeline

`bounty/scanner.py` → scope → recon → hunt → report. Submit: `/approve bounty <id>`.
