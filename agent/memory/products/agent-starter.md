# Personal Stack Agent Starter — Product Listing

> Status: **publish-ready v0.4** — delivery via **crypto checkout (USDT)** or manual Telegram; Lane A4.  
> Payout: см. `agent/memory/lessons/payout_ru_crypto_first.md` — Gumroad/Lemon/PayPal/Stripe **не используются**.

## Product name

**Personal Stack Agent Starter** — self-hosted AI agent harness for Telegram + daily automation

## Tagline (short)

Deploy your own Cursor-powered agent on a VPS: orchestrator, finance scan, site deploy, memory — no SaaS lock-in.

## Price

- **Launch:** $19 USDT (intro, first 20 sales)
- **Regular:** $29 USDT
- **Updates:** 6 months included; optional $9/yr maintenance tier later

## Cover image brief

- Dark terminal + Telegram chat mockup
- Badge: "Self-hosted · Docker · Python"
- Colors: slate + blue accent (match mpeshekhonov.ru)

## Description (listing body)

### Stop renting agent platforms — run your own harness

This starter kit is a **production-tested template** extracted from a real self-hosted stack: Next.js portfolio site, Python orchestrator, Telegram bot, daily agent cycle, finance paper-trading module, and bug-bounty draft pipeline.

You get the **architecture and wiring**, not a black-box SaaS. Everything runs on **your VPS** with Docker and systemd. Secrets stay in `secrets/` — never in git.

### What's included

| Module | What it does |
|--------|----------------|
| **Orchestrator** | Daily cycle: health → plan → bounded execute → validate → memory log |
| **Telegram bot** | `/task`, `/ask`, `/status`, `/bounty`, approval gates |
| **Cursor bridge** | SDK integration for autonomous coding tasks |
| **Finance harness** | Multi-venue scan, risk engine, paper-trade JSON proposals |
| **Site pipeline** | Next.js 15 portfolio + `deploy-from-git.sh` |
| **Memory system** | Markdown daily logs + SQLite state |
| **Docs** | Bootstrap server, secrets layout, autonomy matrix |

### Who this is for

- Developers who want **full control** over agent prompts, logs, and deploy
- Indie hackers building a **personal ops stack** (site + bot + cron)
- Teams prototyping **human-in-the-loop** automation (approve before submit/trade)

### Who this is NOT for

- Non-technical users expecting plug-and-play without a VPS
- People looking for guaranteed trading profits (finance is paper-first + risk-gated)
- Enterprise compliance-heavy deployments (no SOC2 pack included)

### Requirements

- Ubuntu VPS (2 GB RAM minimum, 4 GB recommended)
- Domain + HTTPS (Caddy example included)
- Cursor API key
- Telegram bot token
- Basic Docker + git comfort

### Setup time

~2–4 hours first deploy with docs; daily cycle runs unattended after bootstrap.

### License

Personal / single-server use. No resale of the template as-is. Commercial use on your own infrastructure OK.

---

## FAQ (for listing)

**Q: Does this include Cursor subscription?**  
A: No — you bring your own Cursor API key.

**Q: Is finance trading live by default?**  
A: No. `FINANCE_LIVE=false` until you explicitly enable it in Telegram.

**Q: How do I pay?**  
A: USDT via crypto checkout on mpeshekhonov.ru (NOWPayments/Cryptomus — IB-16) or manual Telegram invoice.

**Q: Updates?**  
A: Changelog in repo; buyers get download link or zip refresh for 6 months.

**Q: Support?**  
A: Email + Telegram community link (optional). No SLA on intro price.

---

## Checkout & delivery checklist

- [x] Buyer bootstrap doc: `agent/memory/products/delivery-readme.md`
- [x] File delivery: `scripts/bundle-agent-starter.sh` → `dist/personal-stack-agent-starter-v0.3.tar.gz`
- [x] Pre-flight: `scripts/verify-agent-starter-bundle.sh` (no secrets leak)
- [ ] **IB-16:** Crypto checkout webhook on site → auto delivery link after USDT payment
- [ ] Product page CTA: crypto checkout URL (replace Telegram early-access)
- [ ] Email receipt: link to bootstrap docs + download

### Manual delivery (until IB-16 live)

1. Buyer pays USDT to seller wallet (Telegram invoice)
2. Seller runs `bundle-agent-starter.sh`, sends secure download link
3. Log sale: `python3 -m finance.a4_sales --net-usd <net> --order-id CRYPTO-<id>`

---

## Launch notes (agent-maintained)

- [x] Cross-link from blog post «Self-hosted agent stack»
- [x] ProductTeaser CTA on homepage (pre-launch → Telegram early access)
- [ ] Add crypto checkout URL to ProductTeaser when IB-16 live
- [x] Track sales in `finance_log` as lane A4 — `python3 -m finance.a4_sales --net-usd 17.10 --order-id CRYPTO-xxx`
- [x] v0.3: `bundle-agent-starter.sh` strips secrets/state/VPN creds
- v0.4: platform-agnostic listing docs (IB-17); v0.5: crypto checkout webhook (IB-16)

## Internal refs

- Source stack: `/opt/personal-stack`
- Income lane: A4 in `agent/memory/income_plan.md`
- Payout constraints: `agent/memory/lessons/payout_ru_crypto_first.md`
