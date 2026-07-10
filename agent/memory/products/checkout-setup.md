# A4 Crypto Checkout — Setup (IB-16)

> Lane A4 · USDT via NOWPayments or Cryptomus · auto delivery link after payment

## Architecture

```text
Buyer pays USDT → IPN webhook (/api/checkout/ipn) → HMAC delivery token
  → GET /api/checkout/delivery?token=… → bundle zip
  → agent: python3 -m finance.checkout_sync → finance_log (M1)
```

## 1. Secrets

```bash
cp secrets/.env.checkout.template secrets/.env.checkout
chmod 600 secrets/.env.checkout
openssl rand -hex 32   # → CHECKOUT_DELIVERY_SECRET
```

Fill provider credentials (at least one):

| Provider | Dashboard | Webhook URL |
|----------|-----------|-------------|
| **NOWPayments** | account.nowpayments.io | `https://mpeshekhonov.ru/api/checkout/ipn` |
| **Cryptomus** | cryptomus.com | `https://mpeshekhonov.ru/api/checkout/ipn?provider=cryptomus` |

## 2. Bundle artifact

```bash
./scripts/bundle-agent-starter.sh --version 0.3
./scripts/verify-agent-starter-bundle.sh
```

Ensure `dist/personal-stack-agent-starter-v0.3.tar.gz` exists before deploy (zip fallback if `zip` CLI available).

## 3. Deploy

`docker-compose.yml` mounts:

- `./dist` → `/app/delivery` (read-only bundle)
- `./data/checkout` → `/app/data/checkout` (orders JSON, shared with agent)
- `secrets/.env.checkout` via `env_file`

```bash
./scripts/redeploy-site.sh
./scripts/verify-checkout-readiness.sh
curl -s https://mpeshekhonov.ru/api/checkout/ipn | jq .
# → {"configured": true, ...} when secrets are set
```

## 4. Create payment (manual until invoice API)

1. NOWPayments dashboard → create payment link for **$19 USDT** (intro) or **$29**
2. Share link on site / Telegram
3. On `finished` IPN, response JSON includes `delivery_url`

## 5. Log sale to M1

After IPN fulfillment:

```bash
cd agent && PYTHONPATH=. python3 -m finance.checkout_sync
# or dry-run:
python3 -m finance.checkout_sync --dry-run
```

Manual fallback:

```bash
python3 -m finance.a4_sales --net-usd 17.1 --order-id NP-<payment_id>
```

## 6. Homepage CTA (manual)

When live: add checkout link to homepage or blog post — **not** autonomous daily change.

## Checklist

- [ ] `secrets/.env.checkout` filled
- [ ] Bundle in `dist/`
- [ ] `./scripts/verify-checkout-readiness.sh` passes
- [ ] IPN test from provider sandbox → `data/checkout/orders.json`
- [ ] Delivery download works with token
- [ ] `checkout_sync` logs to `finance_log`
