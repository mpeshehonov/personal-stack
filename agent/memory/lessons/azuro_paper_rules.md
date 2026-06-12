# Azuro Paper-Trade Rules (Phase 0)

Hard rules for paper trades before any live Azuro orders. Enforced in code via `finance/signal_rules.py` and `finance/risk_engine.py`.

## Edge & drift

| Rule | Default | Env override |
|------|---------|--------------|
| Minimum edge vs reference | **3.0%** | `AZURO_MIN_EDGE_PCT` |
| Maximum odds drift since baseline | **5.0%** | `AZURO_MAX_ODDS_DRIFT_PCT` |

- **Edge:** only trade when modeled or cross-book delta ≥ min edge. Markets without `edge_pct` pass the filter until a model is wired (paper week collects baseline).
- **Drift:** reject if `odds_drift_pct` on the market exceeds max. No baseline yet → filter skipped.

## Liquidity

| Rule | Default | Env override |
|------|---------|--------------|
| Minimum market turnover (USD) | **$100** | `AZURO_MIN_TURNOVER_USD` |

Skip prematch games with turnover below floor. Missing turnover → reject (fail closed for Azuro).

## League whitelist

Only major leagues until paper stats justify expansion:

- Football: Premier League, La Liga, Serie A, Bundesliga, Ligue 1, UEFA Champions League, UEFA Europa League
- US sports: NBA, NHL, NFL, MLB

Override comma-separated list: `AZURO_LEAGUE_WHITELIST=Premier League,NBA,...`  
Empty value disables league filtering.

## Risk caps (all venues)

From `.env.finance` — not Azuro-specific:

- `FINANCE_LIVE=false` until explicit user Telegram approval
- `MAX_TRADE_USD` (default 75), `DAILY_STOP_LOSS_USD` (default 100)
- `MAX_OPEN_POSITIONS` (default 3)

## Paper week (IB-03)

Run **7 consecutive days** with `FINANCE_VENUES=azuro,cex`:

1. Log scan counts by venue in daily Finance section
2. Log paper trades to `finance_log` (count, total USD, by venue)
3. After day 7: go/no-go note in `agent/memory/lessons/` for live Azuro

**Kill criteria:** paper expectancy ≤ 0 after 7 days → pivot primary lane to signals (A3) + digital product (A4).

## Live trading blockers

Do **not** set `FINANCE_LIVE=true` until:

1. 7-day paper complete with positive expectancy
2. `OPERATIONAL_WALLET_PRIVATE_KEY` + USDC on Polygon configured
3. Azuro `place_order` wired to `POST /bet/orders/ordinar` + SIWE (currently stub)
4. Go/no-go note written and user approves via Telegram
