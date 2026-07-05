# Shopify bug bounty playbook (HackerOne)

Use when `{program_name}` is **Shopify** or team_handle is `shopify`.

**Last scope sync:** 2026-07-05 (BB-04) — public policy + dev-store API smoke test. Re-check HackerOne policy monthly.

## Policy gates (must follow)

Source: [HackerOne Shopify](https://hackerone.com/shopify), [Getting started](https://www.shopify.com/bugbounty/resources/getting-started-in-our-bug-bounty-program), Shopify SECURITY.md.

1. **Own stores only** — test only shops you created via [partners.shopify.com/signup/bugbounty](https://partners.shopify.com/signup/bugbounty). Never touch live merchants.
2. **H1 email alias** — Partner/dev-store email must use your `@wearehackerone.com` alias tied to the HackerOne account.
3. **Submit via HackerOne only** — no Shopify Support chat/email/phone about reports.
4. **No commercial scanners** (Nessus etc.), no DoS/brute-force/spam.
5. **Bounty calculator (since 2025-01-28 ET):** reports triaged with Shopify's updated CVSS-style calculator — emphasize cross-asset / subsequent-system impact in write-ups. See [calculator FAQ](https://shopify.github.io/appsec/cvss_calculator/).

## In-scope surfaces (verify on H1 before each hunt)

| Tier | Asset | Dev-store test path | Notes |
|------|-------|---------------------|-------|
| P0 | `*.myshopify.com/admin` | Your dev store Admin (REST + GraphQL) | Core store app; IDOR/RBAC primary |
| P0 | Admin GraphQL / REST | `admin/api/2024-10/` on **your** shop | Shop-scoped mutations; bulk ops, webhooks |
| P1 | `admin.shopify.com` | Org-level admin if your Partner account has access | Staff/collaborator flows |
| P1 | Partners dashboard | partners.shopify.com | OAuth apps you own |
| P1 | Storefront / Checkout | Your dev store checkout, discounts, gift cards | Logic bugs on **your** cart only |
| P2 | Custom/public apps | dev.shopify.com app + OAuth install on your store | redirect_uri, token leakage |
| P2 | Themes / Liquid | Theme editor on your store | Only if demonstrably security-relevant |

**Out of scope (usually):** third-party apps you don't own, Shopify Plus-only without access, merchant stores you didn't create, rate limits without impact, scanner noise, social engineering.

## Dev-store auth (2026 — Dev Dashboard)

Apps in **dev.shopify.com** use **Client ID + Client secret** → **24h** Admin API token via `client_credentials` grant ([docs](https://shopify.dev/docs/apps/build/dev-dashboard/get-api-access-tokens)).

`secrets/.env.bounty`:

```bash
SHOPIFY_SHOP1_DOMAIN=your-test.myshopify.com
SHOPIFY_SHOP2_DOMAIN=your-second-test.myshopify.com   # required for cross-shop IDOR
SHOPIFY_APP_CLIENT_ID=...
SHOPIFY_APP_CLIENT_SECRET=shpss_...
# Optional legacy: SHOPIFY_SHOP1_ADMIN_TOKEN=shpat_...
```

Verify before hunt:

```bash
cd /opt/personal-stack/agent
python3 -m bounty.shopify_token --shop 1   # must succeed
python3 -m bounty.shopify_token --shop 2   # required for IDOR across shops
curl -sS -o /dev/null -w "%{http_code}" \
  -H "X-Shopify-Access-Token: $(python3 -m bounty.shopify_token --shop 1)" \
  "https://YOUR_SHOP.myshopify.com/admin/api/2024-10/shop.json"   # expect 200
```

**Common errors:** `shop_not_permitted` — app not installed on store or org mismatch.

### Stack status (2026-07-05)

| Check | Status |
|-------|--------|
| Shop 1 domain + Admin API | OK (smoke test 200) |
| Shop 2 for cross-shop IDOR | **Missing** — add `SHOPIFY_SHOP2_DOMAIN` + install same app |
| Token path | static `shpat_*` or client_credentials cache |

## Test stores

Create **two** dev stores under your Partner account. Never touch merchant data you do not own. Cross-shop IDOR hypotheses **blocked** until shop 2 is configured.

## Hypothesis templates (pick 3+ per hunt)

| # | Technique | Example |
|---|-----------|---------|
| 1 | GraphQL IDOR | Mutate `gid://shopify/Order/...` across shop contexts (needs 2 stores) |
| 2 | OAuth redirect | `redirect_uri` open redirect / token leak in app install |
| 3 | Webhook SSRF | Register webhook URL pointing to your canary |
| 4 | Discount logic | Stack incompatible discounts on checkout |
| 5 | Staff RBAC | Lower-privilege staff accessing admin-only mutations |
| 6 | Bulk/export abuse | Admin bulk ops leaking other-shop identifiers |
| 7 | File upload | Theme/asset upload content-type or path issues |

## Evidence bar

- `confirmed` only with reproducible HTTP request + response on **your** assets
- Redact `X-Shopify-Access-Token`, client secrets, and PII in drafts
- Include shop domain, API version, request/response snippets
- Impact: cross-shop data access, payment, or account takeover — not informational misconfig
- For medium+ severity under 2025 calculator: document **subsequent system** impact (confidentiality/integrity/availability on assets beyond the vulnerable component)

## Report export

Submit via HackerOne API after `/approve bounty <id>`. For manual platforms see `bounty/submit.py` export — Shopify uses HackerOne auto-submit when configured.
