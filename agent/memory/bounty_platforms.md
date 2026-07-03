# Bug bounty platforms — catalog (agent-maintained)

> **Goal:** white-hat pentest → semi-auto submit-ready reports → **payout in crypto** where possible (RU-resident friendly).  
> Orchestrator rotates programs; daily agent **extends this file**, does not duplicate hunt.

## Priority tiers

### P0 — crypto payout likely (research & add programs)

| Platform | URL | Payout | Fit (web/JS) | Agent action |
|----------|-----|--------|--------------|--------------|
| **Immunefi** | https://immunefi.com/ | USDC/USDT (on-chain) | Web3 + often web2 adjacent | Scan programs with web/API scope; add to rotation |
| **HackenProof** | https://hackenproof.com/ | Crypto | Web, exchange, SaaS | Register programs with public scope |
| **Cantina** | https://cantina.xyz/ | Crypto (audits/competitions) | Smart contracts + web | Competitions when open |
| **Code4rena** | https://code4rena.com/ | USDC | Audit contests | JS/TS repos when listed |

### P1 — established; verify payout method for RU

| Platform | URL | Payout | Notes |
|----------|-----|--------|-------|
| **HackerOne** | https://hackerone.com/ | Bank / PayPal / **crypto (check account)** | Already integrated (`submit.py`); Shopify focus |
| **Bugcrowd** | https://bugcrowd.com/ | Varies | Mozilla in `programs.py` |
| **Intigriti** | https://intigriti.com/ | Bank (EU) | IKEA in rotation |
| **YesWeHack** | https://yeswehack.com/ | Bank/PayPal | EU programs |
| **Synack** | https://synack.com/ | USD | Invite-only |
| **OpenBugBounty** | https://openbugbounty.org/ | Reputation / optional tips | Low $; good for practice |

### P2 — other vectors (document only)

| Vector | Notes |
|--------|-------|
| **GitHub Security Lab / private disclosures** | No platform fee; slow; responsible disclosure |
| **Vendor VDP** (Google, Meta, Microsoft) | Often HackerOne/Bugcrowd backend |
| **CVE / GHSA mining** | **Avoid** — purge queue treats as spam |
| **Shopify dev stores** | HackerOne Shopify — primary web/JS niche |

## Payout rails (agent-researched)

> **Updated:** 2026-07-03 (BB-02). Sources: Immunefi/HackenProof help docs, platform program pages.  
> **Account status:** Immunefi + HackenProof — **не зарегистрированы** (user action). HackerOne — API в `secrets/.env.bounty`, crypto payout **не проверен** в настройках аккаунта.

| Platform | Payout rail | Currency / chain | RU fit | Setup before first payout | Auto-submit (`submit.py`) | Notes |
|----------|-------------|------------------|--------|---------------------------|---------------------------|-------|
| **Immunefi** | **Crypto (on-chain)** | USDC/USDT; chain per program (often Ethereum, Arbitrum, Base) | **✅ High** | Account + [wallet verify](https://bugs.immunefi.com/settings/wallets-and-payments) (sign message); wallet at report submit | ❌ Manual (BB-03) | Project pays directly after Confirmed→Paid; rewards USD-denominated, settled in stablecoin; non-EVM chains negotiated per report |
| **HackenProof** | **Crypto (custodial balance → withdraw)** | **USDC on Base** (~95% programs); per-program: ETH, BTC, native tokens | **✅ High** | Account + 2FA + external wallet in profile; min withdraw **100 USDC** | ❌ Manual (BB-03) | Balance credited after triage; withdraw ≤48 business hours; KYC+invoice path for tax docs (EU residents: invoice-only) |
| **HackerOne** | Bank / PayPal / **crypto (account setting)** | USD; crypto if enabled on researcher profile | **⚠️ Verify** | API token in `secrets/.env.bounty`; enable crypto in payout settings if available | ✅ `submit_hackerone()` | Primary Shopify lane; bank/PayPal poor for RU — **prefer crypto toggle** before relying on payouts |
| **Bugcrowd** | Varies (often bank/PayPal) | USD, gift cards, crypto on select programs | **⚠️ Low–Med** | Per-program enrollment | ❌ Manual | Mozilla in rotation; check program reward terms |
| **Intigriti** | Bank (EU SEPA) | EUR | **❌ Poor** | EU bank account typical | ❌ Manual | IKEA in rotation — background only for RU |
| **Cantina** | Crypto | USDC (competitions) | **✅ Med** | Account + wallet per competition | ❌ Manual | Audit contests; episodic |
| **Code4rena** | Crypto | USDC | **✅ Med** | GitHub + wallet per contest | ❌ Manual | Smart-contract contests; JS repos when listed |

### Wallet alignment (north star)

Target: same operational wallet as `YOUR_WALLET_ADDRESS` in `secrets/.env.finance` (Bybit deposit or EVM address).

| Platform | Recommended wallet config |
|----------|---------------------------|
| Immunefi | EVM address (MetaMask/Bybit on-chain) — verify on settings page; match chain to program (0x/edgeX → check program page) |
| HackenProof | USDC **Base** address — Bybit supports Base USDC deposit, or MetaMask |
| HackerOne | Enable crypto payout in account if available; else treat as M2/M3 backup only |

### User account checklist (blocks first crypto payout)

- [ ] Register **Immunefi** — add + verify default payout wallet
- [ ] Register **HackenProof** — enable 2FA, add USDC (Base) withdraw wallet
- [ ] **HackerOne** — confirm crypto payout option in Payment Preferences (not just API for submit)

## Rotation source of truth

Curated list for scanner: `agent/bounty/programs.py` (`WEB_JS_PROGRAMS`).

When adding a program:
1. Verify **in-scope** assets on platform policy page.
2. Note **payout rail** (crypto preferred) in `notes`.
3. Prefer programs matching stack: React, Next, GraphQL, OAuth, IDOR, SSRF, payment APIs.

## Weekly agent task (orchestrator + daily)

- [x] Add ≥1 new program from P0/P1 with crypto or confirmed payout path (2026-07-02: 0x, edgeX, Backpack)
- [ ] Mark dead programs (out of scope, duplicate, zero response) in `## Dead programs` below
- [ ] Summarize in daily `## Баг-баунти`: programs tried, drafts pending, payout blockers

## Dead programs

_(none yet)_

## Decision log

| Date | Note |
|------|------|
| 2026-07-03 | BB-02: payout rails table + wallet alignment + account checklist (Immunefi/HackenProof public docs) |
| 2026-07-02 | BB-01: +3 programs in `programs.py` — 0x/Matcha, edgeX (Immunefi, USDC); Backpack (HackenProof, USDC Base) |
| 2026-06-23 | User: no PayPal/Stripe; focus bounty until wallet funded; expand beyond HackerOne-only |
