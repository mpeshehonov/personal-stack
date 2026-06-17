# Shopify bug bounty playbook (HackerOne)

Use when `{program_name}` is **Shopify** or team_handle is `shopify`.

## High-value surfaces (verify in-scope on HackerOne policy first)

1. **Admin / Partners**
   - `admin.shopify.com`, Partners dashboard, OAuth apps
   - IDOR: shop_id, order_id, customer_id, staff permissions across shops you own
2. **Storefront / Checkout**
   - Cart, checkout extensions, discount codes, gift cards on **your** dev stores
   - Logic bugs: price manipulation, race on inventory, checkout bypass
3. **APIs**
   - Admin GraphQL + REST on dev stores — test auth boundaries, bulk operations, webhooks
   - GraphQL introspection abuse, excessive data exposure, missing shop scoping
4. **Apps & Themes**
   - Public app OAuth flow, redirect_uri validation, token leakage
   - Liquid/theme sandbox escapes (only if in scope)
5. **Collaborator / staff invites**
   - Permission escalation between staff roles on test shops

## Test stores

Create **two** dev stores under your Partner account. Never touch merchant data you do not own.

## Hypothesis templates (pick 3+ per hunt)

| # | Technique | Example |
|---|-----------|---------|
| 1 | GraphQL IDOR | Mutate `gid://shopify/Order/...` across shop contexts |
| 2 | OAuth redirect | `redirect_uri` open redirect / token leak in app install |
| 3 | Webhook SSRF | Register webhook URL pointing to your canary |
| 4 | Discount logic | Stack incompatible discounts on checkout |
| 5 | Staff RBAC | Lower-privilege staff accessing admin-only mutations |
| 6 | File upload | Theme/asset upload content-type or path issues |

## Evidence bar

- `confirmed` only with reproducible HTTP request + response on **your** assets
- Include `X-Shopify-Access-Token` redacted, shop domain, API version
- Impact: cross-shop data access, payment, or account takeover — not informational misconfig

## Out of scope (usually)

- Shopify Plus-only without access, third-party apps not yours, social engineering, rate limit without impact, scanner noise.
