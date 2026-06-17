# Azuro Live — Go/No-Go (IB-04)

**Date:** 2026-06-17  
**Paper week:** 7/7 complete (2026-06-11 → 2026-06-17)

## Summary

**Decision: NO-GO for Azuro live trading.**

Do not enable `FINANCE_LIVE=true` for Azuro until blockers below are resolved and a new paper week shows tradeable Azuro markets with positive modeled edge.

## Paper week stats

| Day | Trades | USD exposure | Tradeable venue |
|-----|--------|--------------|-----------------|
| 2026-06-11 | 3 | $75 | CEX only |
| 2026-06-12 | 3 | $75 | CEX only |
| 2026-06-13 | 9 | $225 | CEX only |
| 2026-06-14 | 9 | $225 | CEX only |
| 2026-06-15 | 12 | $300 | CEX only |
| 2026-06-16 | 6 | $150 | CEX only |
| 2026-06-17 | 3 | $75 | CEX only |
| **Total** | **45** | **$1,125** | **0 Azuro** |

- Daily scan: **13** markets (azuro 10 + cex 3) → **3** tradeable (100% CEX)
- Azuro rejections: liquidity floor, league whitelist, missing edge model — **0 Azuro paper fills**
- Logged exposure is not realized PnL; no expectancy signal for Azuro

## Blockers (must fix before re-evaluating)

1. **No Azuro paper validation** — filters reject all Azuro markets; edge model not wired (`edge_pct` absent)
2. **`place_order` stub** — `POST /bet/orders/ordinar` + SIWE not implemented
3. **Wallet** — `OPERATIONAL_WALLET_PRIVATE_KEY` + USDC on Polygon not confirmed in daily ops
4. **M1 definition** — even if live worked, current loop produces CEX exploratory buys, not Azuro value bets

## Recommended pivot (per kill criteria in azuro_paper_rules.md)

| Priority | Lane | Action |
|----------|------|--------|
| **Primary** | **A2 CEX grid** | Continue read-only grid calculator; next step: paper grid simulation or small live grid after user approves capital |
| **Secondary** | **A3 Signals** | Configure `TELEGRAM_SIGNAL_CHANNEL_ID`; publish top-3 scan (helper ready) |
| **Background** | **A4 Product** | IB-08 Gumroad listing draft |
| **Defer** | **A1 Azuro live** | Revisit after edge model + league/liquidity tuning yields ≥1 tradeable Azuro market/day in paper |

## Re-evaluation criteria

Re-run 7-day paper when:

- Azuro markets pass `signal_rules.py` with `edge_pct` from a reference model
- `place_order` implemented and tested on testnet or min size
- User explicitly approves live via Telegram

Until then: **keep `FINANCE_LIVE=false`.**
