# Bounty Backlog — Agent-Pickable Tasks

Aligned with `agent/memory/bounty_platforms.md` and `agent/skills/bounty-harness/SKILL.md`.  
**Orchestrator** runs hunt (`bounty/scanner.py`); **daily agent** picks **≤1 item** here when no income_backlog item is higher priority.

## Phase 0 — Platform expansion (current)

- [x] **BB-01** Add 2+ Immunefi/HackenProof programs to `agent/bounty/programs.py` (web/API scope, crypto payout noted)
- [x] **BB-02** Document payout rails per platform in `agent/memory/bounty_platforms.md` (after account checks)
- [x] **BB-03** Extend `Platform` type + `submit.py` stub for one non-HackerOne platform (Immunefi or HackenProof report export)
- [x] **BB-04** Shopify playbook refresh — verify HackerOne scope still matches dev-store flow (`agent/tasks/bounty_shopify_playbook.md`)

## Phase 1 — Quality & throughput

- [x] **BB-05** `finance/bounty_payout.py` — log accepted bounty rewards to `finance_log` (mirror `a4_sales.py`)
- [x] **BB-06** Weekly program suggestion in daily log: rotate away from low-response programs
- [x] **BB-07** Leads pipeline: tag `[Lead]` drafts with `payout_rail: crypto|bank|unknown`

## Phase 2 — Crypto rotation (ongoing)

- [x] **BB-08** Add ≥1 Immunefi web/API program with USDC/USDT payout to `programs.py` + note in `bounty_platforms.md` (2026-07-16: GMX)
- [x] **BB-09** Add ≥1 Immunefi dedicated web program with USDC payout to `programs.py` + note in `bounty_platforms.md` (2026-07-17: 1inch Web)
- [x] **BB-10** Add ≥1 Immunefi Web & App program with USDC payout + NextJS/web stack fit to `programs.py` + note in `bounty_platforms.md` (2026-07-18: ENS)
- [x] **BB-11** Add ≥1 Immunefi Web & App program with USDC/USDT payout + no KYC to `programs.py` + note in `bounty_platforms.md` (2026-07-19: Lido)
- [x] **BB-12** Add ≥1 Immunefi Web & App program with crypto-stable payout (DAI/USDS) + no KYC to `programs.py` + note in `bounty_platforms.md` (2026-07-20: Sky)

## Rules

1. **No live exploit** against production without scope — dev stores / staging only where allowed
2. Submit only after user `/approve bounty <id>`
3. Do not duplicate orchestrator hunt in daily cycle
4. GHSA/CVE template spam → purge, not submit
5. Prefer programs with **crypto payout** for RU-resident user
