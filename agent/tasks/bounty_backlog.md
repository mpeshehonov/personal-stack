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
- [ ] **BB-07** Leads pipeline: tag `[Lead]` drafts with `payout_rail: crypto|bank|unknown`

## Rules

1. **No live exploit** against production without scope — dev stores / staging only where allowed
2. Submit only after user `/approve bounty <id>`
3. Do not duplicate orchestrator hunt in daily cycle
4. GHSA/CVE template spam → purge, not submit
5. Prefer programs with **crypto payout** for RU-resident user
