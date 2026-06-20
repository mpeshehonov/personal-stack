# M1 Milestone Review — 2026-06-20 (IB-11)

## Snapshot

| Metric | Value |
|--------|-------|
| M1 target | $1,000 net autonomous by 2026-09-30 |
| Earned (realized PnL) | **$0** |
| Progress | **0%** |
| Days left | 101 (~$9.90/day needed) |
| Annual goal | $0 / $15,000 (193 days) |

## Lane status

| Lane | Autonomy | Status | M1 contribution |
|------|----------|--------|-----------------|
| **A1 Azuro** | 85% | **NO-GO** (see `azuro_live_gonogo.md`) — 0 tradeable markets | Blocked |
| **A2 CEX grid** | 90% | Paper scan active; grid calculator ready; **no live capital** | Primary candidate |
| **A3 Signals** | — | **Cancelled** (2026-06) | — |
| **A4 Product** | 80% | Gumroad draft ready (`agent-starter.md`); not listed | Zero-capital unlock |
| **A5 Affiliate** | 85% | Blog skeleton draft (`cex-grid-trading-bybit.md`); not published | Long tail |
| **A7 Bounty** | 35% | M2 lane; orchestrator drafts only | Not M1 |

## Paper trading (cumulative)

- **69** paper trades, **$1,725** logged exposure (not PnL)
- **100% CEX** exploratory buys ($25 × 3/day)
- **0 Azuro** fills — filters reject all 10 scanned markets daily
- Grid previews: BTC/ETH/SOL @ $300 capital, 5 levels, 10% span

## Capital / venue reallocation proposal

### Immediate (no live trading)

1. **A4 — Publish Gumroad listing** ($0 capital, ~80% autonomous after setup)
   - Product ready: Personal Stack Agent Starter @ $19 intro
   - One sale/week ≈ $76/mo — slow but counts toward M1 if autonomous checkout

2. **A5 — Publish affiliate blog draft** ($0 capital)
   - Replace `YOUR_AFFILIATE_ID` placeholders → set `draft: false`
   - Drives long-tail traffic; not sufficient alone for $1k by Sep

### Requires user approval (`FINANCE_LIVE=true`)

3. **A2 — CEX grid live on BTCUSDT** ($300–400 USDT recommended)
   - Rationale: only lane with validated scan + grid params; Azuro blocked
   - Params: 5 levels, 10% span, ~$60/level (from today's grid preview)
   - Risk caps unchanged: `MAX_TRADE_USD=75`, `DAILY_STOP_LOSS_USD=100`
   - **Do not enable** until user Telegram approval

4. **A1 — Defer** until edge model wired and ≥1 Azuro market passes filters in paper

### Deprioritize for M1

- **A7 Bounty (IB-10):** valuable for M2 ($5k), not autonomous enough for M1
- **A8 Freelance / A9 Job hunt:** manual approval lanes, M3 only

## Recommended portfolio shift

```
Before (plan):  A1 primary + A2 parallel + A4/A5 background
After (review): A2 primary (pending live approval) + A4 immediate + A5 publish + A1 deferred
```

## Decision gates

| Gate | Condition |
|------|-----------|
| CEX live | User `/approve` or `FINANCE_LIVE=true` + $300 USDT on Bybit |
| Azuro re-eval | New 7-day paper after edge model + place_order impl |
| M1 Phase 2 bounty | M1 > 30% or explicit user redirect to IB-10 |

## Next cycle priorities

1. Publish A4 on Gumroad (listing + payment link)
2. Publish A5 affiliate post (real ref IDs)
3. User decision on $300 CEX grid capital
4. IB-10 Shopify bounty prep (orchestrator hunt lane) when M2 focus starts
