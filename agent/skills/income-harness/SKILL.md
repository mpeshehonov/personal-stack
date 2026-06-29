---
name: income-harness
description: Income lanes for personal-stack — bounty-first (crypto payout), A4 crypto product, deferred trading. Use during daily finance/income section.
---

# Income Harness

Load when working on `agent/tasks/income_backlog.md`, `agent/tasks/bounty_backlog.md`, or finance section.

## North star

**Realized profit → operational crypto wallet (USDT/USDC).**  
RU constraints: `agent/memory/lessons/payout_ru_crypto_first.md` — **no Gumroad/Lemon/PayPal/Stripe**.

## M1 goal

**$1,000 net to wallet by 2026-09-30** — see `agent/memory/income_plan.md` (2026-06-23 pivot).

## Active lanes (priority)

1. **A7 Bug bounty** — orchestrator hunt; user `/approve bounty`; expand `bounty_platforms.md`
2. **A4 Digital product** — bundle ready; **IB-16 crypto checkout** (not Gumroad)
3. **A5 Affiliate** — background blog posts
4. **A1/A2 Trading** — **deferred** until wallet funded; paper optional, no live proposals

## Does NOT count / blocked

- Gumroad/Lemon MoR listings
- `FINANCE_LIVE` without capital + user approve
- Manual salary (A8) for autonomy metrics

## Validation

- Append stats to `## Финансы` and `## Баг-баунти` in daily log
- Update backlog `[x]` when task complete
- Log sales: `python3 -m finance.a4_sales`; bounty payouts → BB-05 when implemented

## Kill criteria

- Do not spend daily cycles on Azuro/CEX backlog while BB-* items open
- Never enable live without user Telegram approval **and** wallet balance
