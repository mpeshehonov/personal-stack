# Income Backlog — Agent-Pickable Tasks

Tasks aligned with `agent/memory/income_plan.md`. Pick **at most 1 income task per day** (plus existing daily priorities).

## Phase 0 — Validation

- [x] **IB-01** Enable multi-venue scan: verify `azuro_client.py` + `cex_client.py` return markets from NL VPS; log in daily Finance section
- [x] **IB-02** Document paper-trade rules in `agent/memory/lessons/azuro_paper_rules.md` (min edge %, max drift, league whitelist)
- [x] **IB-03** Run 7 consecutive days paper; append stats to daily log (count, total USD, by venue)
- [x] **IB-04** After day 7: write go/no-go note for Azuro live in `agent/memory/lessons/`

## Phase 1 — M1 lanes

- [x] **IB-05** Azuro: add simple rule filter in finance scan (skip markets below liquidity / above odds drift) — code change in executor or new `finance/signal_rules.py`
- [x] **IB-06** CEX: implement read-only grid parameter calculator (grid levels, not live orders yet)
- [x] **IB-07** ~~A3 signals: Telegram channel~~ — helper shipped (`signal_post.py`); **lane cancelled**, do not configure `TELEGRAM_SIGNAL_CHANNEL_ID`
- [x] **IB-08** A4 product: draft Gumroad listing copy in `agent/memory/products/agent-starter.md`
- [x] **IB-09** A5 affiliate: one blog post skeleton under `site/content/blog/` (if dir missing, create minimal MD route)

## Phase 2 — Scale (after M1 progress >30%)

- [ ] **IB-10** Bounty: Shopify deep-dive with dev-store Admin API tokens (see `agent/skills/bounty-shopify/`)
- [x] **IB-11** Review milestone progress; propose capital / venue reallocation in daily Summary
- [x] **IB-12** A5: publish affiliate blog post (`cex-grid-trading-bybit.md`, `draft: false`, plain links until ref IDs in secrets)
- [x] **IB-13** A4: publish-ready Gumroad bundle (`delivery-readme.md`) + site ProductTeaser CTA
- [x] **IB-14** A4: Gumroad delivery zip script (`scripts/bundle-agent-starter.sh`) — strips secrets/state/VPN creds

## Rules

1. Never enable `FINANCE_LIVE=true` without explicit user Telegram message
2. Income tasks do not override site health or security fixes
3. Mark completed items `[x]` in this file when done
