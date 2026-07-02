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
| 2026-07-02 | BB-01: +3 programs in `programs.py` — 0x/Matcha, edgeX (Immunefi, USDC); Backpack (HackenProof, USDC Base) |
| 2026-06-23 | User: no PayPal/Stripe; focus bounty until wallet funded; expand beyond HackerOne-only |
