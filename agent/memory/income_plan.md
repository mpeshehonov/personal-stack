# Income Plan — ARCHIVED / PAUSED (2026-07-20)

> **Status:** paused. Autonomous earning (bounty, trading, A4 crypto product) did not deliver ROI.
> North star is now **career hunter** — see `agent/memory/goals.md`, `docs/career-growth-system.md`.
> Do not pick tasks from this plan in daily cycles. Code in `agent/finance/` and `agent/bounty/` remains offline (`FINANCE_DAILY_SCAN=false`, `BOUNTY_DAILY_SCAN=false`).

---

# (Historical) Income Plan — Milestones & Autonomous Lanes

Context: previous assessment — stack is strong **ops infrastructure**, not a money printer yet. Polymarket blocked from NL VPS; annual **$15k by 2026-12-31** needs a phased plan with a **first autonomous milestone**.

## Milestones

| Stage | Target | Deadline | Definition of "earned" |
|-------|--------|----------|------------------------|
| **M1 — Autonomous floor** | **$1,000 net** | **2026-09-30** | Realized profit logged in `finance_log.pnl_usd` from lanes with **autonomy ≥70%** (see matrix below). No manual trading, no bounty submission by user. |
| **M2 — Scale** | $5,000 net | 2026-11-30 | M1 lanes + semi-auto bounty (user only `/approve bounty`, agent does research/draft). |
| **M3 — Annual** | $15,000 net | 2026-12-31 | All legal lanes; reinvest 50% / withdraw 50% on realized profits. |

**M1 rule:** if a lane needs your hands-on work (coding exploits, client calls, manual orders), it does **not** count toward M1 — only toward M2/M3.

---

## Alternative Lanes — Autonomy Matrix

Scoring: **Autonomy** = % of earning loop runnable without you after one-time setup. **M1 fit** = likelihood of reaching $1k without you by Sep 2026.

| # | Lane | Autonomy | Capital | M1 fit | Stack leverage | Notes |
|---|------|----------|---------|--------|----------------|-------|
| **A1** | **Azuro rule-based value** | 85% | $200–400 USDC | **Deferred** | `azuro_client.py`, risk engine, Polygon wallet | **No seed capital** — paper/log only until wallet funded from A7/A4. Do not propose live. |
| **A2** | **CEX grid / DCA (Bybit NL)** | 90% | $300–600 USDT | **Deferred** | `cex_client.py`, API keys + KYC | Same — **no live grid** until user funds wallet and `/approve`. Paper scan optional in log. |
| **A3** | ~~Cross-venue scan → auto Telegram signals~~ | — | — | **Cancelled** | — | Removed from plan 2026-06 — no public buy-signal channel. Code (`signal_post.py`) stays optional/no-op. |
| **A4** | **Micro digital product (agent-maintained)** | 75% | $0 | Medium | Site, bundle script, payment webhook | Sell "personal-stack agent starter" via **own site + crypto checkout** (USDT). **Not Gumroad/Lemon** — RU resident, no PayPal/Stripe. See `agent/memory/lessons/payout_ru_crypto_first.md`. |
| **A5** | **Affiliate content loop** | 85% | $0 | Low | Site blog, agent daily writes | Posts with Bybit/Azuro/hosting affiliate links. $1k needs traffic; long tail. Background lane only. |
| **A6** | **VPN subscription resale** | 70% | $0 | Low–Med | Existing Hysteria2 stack | Automate sub generation + payment webhook. Legal/ToS risk; not in core goals — **defer** unless explicit decision. |
| **A7** | **Bug bounty (semi-auto pentest)** | 55% | $0 | **High (primary until wallet funded)** | `bounty/scanner.py`, `bounty_platforms.md` | Orchestrator: scope→recon→hunt→submit-ready draft. User: `/approve bounty`. **Payout → crypto wallet** (Immunefi/HackenProof/H1 crypto). Expand platforms — `agent/tasks/bounty_backlog.md`. |
| **A8** | **Freelance / resume funnel** | 10% | $0 | **Not autonomous** | Site, PDF resume | Best $/hour but requires you. Counts toward M3 only. |
| **A9** | **Job Hunt Autopilot** | 45% | $0 | M2/M3 (not M1) | `job_hunt/`, HH API, Telegram approve | Agent finds + scores vacancies, drafts cover letter; **you** `/approve apply`. See `docs/superpowers/specs/2026-06-13-job-hunt-autopilot-design.md`. |

---

## Recommended Portfolio (2026-06-23 pivot — RU, no seed capital)

**North star:** realized profit lands on **operational crypto wallet** (auto/semi-auto). See `agent/memory/lessons/payout_ru_crypto_first.md`.

```
Primary:    A7 Bug bounty (orchestrator hunt + user /approve → crypto payout)
Secondary:  A4 digital product (crypto checkout on site — when IB-16 done)
Background: A5 affiliate (1/week max)
Deferred:   A1/A2 live trading — until wallet funded from A7/A4
```

**Defer:** A6 VPN resale, Gumroad/Lemon MoR, A8 as autonomy metric, Polymarket (geo-blocked from NL).

**M1 note:** strict "≥70% autonomy" lanes (A1/A2 live) **paused** for lack of capital. **Practical M1 path:** first **$1k net to crypto wallet** from A7 (+ A4/A5), logged in `finance_log`, even if semi-auto bounty counts toward M2 in strict scoring.

---

## Phase Plan

### Phase 0 — Bounty + payout path (now)
- [x] Azuro paper go/no-go documented (expectancy ≤ 0)
- [ ] **A7 primary:** ≥3 programs/week in rotation; expand `bounty_platforms.md`
- [ ] Verify crypto payout on HackerOne / register Immunefi or HackenProof
- [ ] **No FINANCE_LIVE** — user has no trading capital

### Phase 1 — Wallet seed (+0 → +90 days)
- [ ] Submit-ready drafts → user `/approve bounty` → first payout to wallet
- [ ] **A4:** crypto checkout webhook (IB-16) — USDT delivery of agent starter bundle
- [ ] Log all external revenue in `finance_log` (bounty + A4)
- [ ] Weekly: PnL vs $1k goal in daily log

### Phase 2 — Reinvest (+after wallet ≥ $300)
- [ ] User approves A2 CEX grid or A1 Azuro live with risk caps
- [ ] Scale only on positive expectancy from logged trades

---

## Lane Details

### A1 — Azuro rule-based value (primary)

**Idea:** Agent scans prematch markets via Backend API; enters only when:
- implied prob vs model (or cross-book) delta ≥ X%
- liquidity above floor
- < N hours to event

**Autonomous loop:** daily scan → JSON proposal → risk engine → wallet sign → log PnL.

**Path to $1k:** ~4% monthly on $400 ≈ 18 months (too slow). Realistic M1 path: **$400 capital + 8–12% monthly** (optimistic) ≈ 6–8 months, OR **larger edge on smaller bank** with strict position sizing.

**Implementation backlog:** see `agent/tasks/income_backlog.md` items IB-01..IB-04.

### A2 — CEX grid / DCA (secondary)

**Idea:** BTC/ETH grid on Bybit NL; parameters fixed in env, not LLM.

**Autonomous loop:** cron/grid bot places limits within risk engine caps.

**Path to $1k:** grid profits are small; treat as **diversifier**, not main bet.

### A3 — ~~Signal bot → paid Telegram~~ (cancelled)

Removed from income plan — no Telegram channel for buy/trade signals. Helper code may remain disabled without `TELEGRAM_SIGNAL_CHANNEL_ID`.

### A4 — Digital product

**Idea:** Package a subset of this repo (or standalone odds scanner) as paid ZIP + docs.

**Autonomous loop:** bundle script → payment webhook → email/TG download link; agent logs sale via `a4_sales.py`.

**Path to $1k:** 50 × $20 USDT — combine with A5 content; **not** Gumroad (RU payout blocked).

### A5 — Affiliate content (background)

**Idea:** Weekly technical post on site (agent-written): "Self-hosted agent stack", "Azuro API notes".

**Autonomous loop:** daily agent picks topic → commit to site → redeploy.

---

## What NOT to count as M1

- Manual bounty submissions (even if agent drafted)
- Salary / Upwork / client work via resume site
- Unrealized paper PnL
- Transfers from your personal wallet (only **external** realized profit)

---

## Env & tracking

```bash
# secrets/.env.finance
MILESTONE_GOAL_USD=1000
MILESTONE_GOAL_DEADLINE=2026-09-30
MILESTONE_GOAL_LABEL=autonomous $1k
FINANCE_VENUES=azuro,cex
```

Progress: `/status` in Telegram shows annual goal + M1 milestone via `goal_tracker.py`.

---

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-12 | M1 = $1k autonomous by Sep 2026 | Realistic first proof before $15k annual |
| 2026-06-12 | A1+A2 portfolio | NL-compatible; uses existing finance module |
| 2026-06-17 | A3 signals cancelled | No TG buy-signal channel; focus A2+A4 |
| 2026-06-12 | Bounty excluded from M1 (strict) | Not autonomous per stack rules |
| 2026-06-23 | **Pivot: A7 primary, A1/A2 live deferred** | RU — no Gumroad/PayPal/Stripe; no crypto seed capital; north star = wallet top-up via bounty + crypto product sales |

---

## Related docs

- `agent/memory/lessons/payout_ru_crypto_first.md` — RU payout constraints, crypto north star
- `agent/memory/bounty_platforms.md` — platform catalog (agent-maintained)
- `agent/tasks/bounty_backlog.md` — bounty pickable tasks
- `agent/memory/trading_alternatives.md` — venue comparison (Azuro, CEX, Overtime)
- `agent/memory/goals.md` — checklist milestones
- `agent/tasks/income_backlog.md` — agent-pickable implementation tasks
