# Income Plan — Milestones & Autonomous Lanes

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
| **A1** | **Azuro rule-based value** | 85% | $200–400 USDC | **High** | `azuro_client.py`, risk engine, Polygon wallet | Closest Polymarket substitute from NL. Needs **7+ days paper** + fixed rules (edge threshold, max odds drift), not LLM guesses. |
| **A2** | **CEX grid / DCA (Bybit NL)** | 90% | $300–600 USDT | Medium | `cex_client.py`, API keys + KYC | Boring but fully API-driven. Small edge; fees eat profit on low capital. Good **parallel** lane while A1 validates. |
| **A3** | ~~Cross-venue scan → auto Telegram signals~~ | — | — | **Cancelled** | — | Removed from plan 2026-06 — no public buy-signal channel. Code (`signal_post.py`) stays optional/no-op. |
| **A4** | **Micro digital product (agent-maintained)** | 80% | $0 | Medium | Site, Cursor agent, deploy pipeline | Sell template: "personal-stack agent starter" / VPN config kit / odds scanner script on Gumroad/Lemon Squeezy. Agent updates README + changelog. One-time sales, slow but truly passive after listing. |
| **A5** | **Affiliate content loop** | 85% | $0 | Low | Site blog, agent daily writes | Posts with Bybit/Azuro/hosting affiliate links. $1k needs traffic; long tail. Background lane only. |
| **A6** | **VPN subscription resale** | 70% | $0 | Low–Med | Existing Hysteria2 stack | Automate sub generation + payment webhook. Legal/ToS risk; not in core goals — **defer** unless explicit decision. |
| **A7** | **Bug bounty (agent-assisted)** | 35% | $0 | Med for M2, **not M1** | `bounty/scanner.py`, curated programs | Scanner + drafts save time; **you** find/submit vulns. One $1k+ report skips M1 definition but hits M2 fast. |
| **A8** | **Freelance / resume funnel** | 10% | $0 | **Not autonomous** | Site, PDF resume | Best $/hour but requires you. Counts toward M3 only. |
| **A9** | **Job Hunt Autopilot** | 45% | $0 | M2/M3 (not M1) | `job_hunt/`, HH API, Telegram approve | Agent finds + scores vacancies, drafts cover letter; **you** `/approve apply`. See `docs/superpowers/specs/2026-06-13-job-hunt-autopilot-design.md`. |

---

## Recommended Portfolio for M1 ($1k autonomous)

Prioritize **two active lanes + one background lane**:

```
Primary:   A1 Azuro (paper → live with risk caps)
Secondary: A2 CEX grid (API-driven diversifier)
Background: A4 digital product + A5 affiliate (1/week)
```

**Defer:** A6 VPN resale, A8 freelance-as-autonomy, Polymarket (geo-blocked from NL).

---

## Phase Plan

### Phase 0 — Validate (now → +7 days)
- [ ] `FINANCE_VENUES=azuro,cex` in finance env
- [ ] 7 days paper on Azuro: log win-rate, avg edge, rule violations
- [ ] CEX: read-only scan running; no live until Azuro paper reviewed
- [ ] Kill criteria: if paper expectancy ≤ 0 after 7 days, pivot primary to **A4** (digital product) + **A2** (CEX grid)

### Phase 1 — M1 execution (+8 → +90 days)
- [ ] Azuro live with `MAX_TRADE_USD≤50`, `DAILY_STOP_LOSS_USD≤75`
- [ ] Deploy **A2** CEX grid read-only / paper params
- [ ] List **A4** product v0.1 (even if $9 — proves autonomous sales loop)
- [ ] Weekly: agent updates `agent/memory/daily/` with PnL vs M1

### Phase 2 — M2 (+91 → +150 days)
- [ ] Add bounty lane: one niche program, agent drafts only
- [ ] Scale what worked in Phase 1 (double capital only on positive expectancy)

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

**Autonomous loop:** agent fixes issues from Gumroad emails; deploy script updates listing version.

**Path to $1k:** 100 sales × $10 or 20 × $50 — needs marketing; combine with A5 content.

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
| 2026-06-12 | Bounty excluded from M1 | Not autonomous per stack rules |

---

## Related docs

- `agent/memory/trading_alternatives.md` — venue comparison (Azuro, CEX, Overtime)
- `agent/memory/goals.md` — checklist milestones
- `agent/tasks/income_backlog.md` — agent-pickable implementation tasks
