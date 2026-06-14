---
name: income-harness
description: Autonomous income lanes for personal-stack — Azuro paper/live rules, CEX scan, signals, digital product, milestone M1. Use during daily finance section or income_backlog tasks.
---

# Income Harness

Load when working on `agent/tasks/income_backlog.md` or finance proposals.

## M1 goal

**$1,000 net autonomous by 2026-09-30** — see `agent/memory/income_plan.md`.

Counts toward M1: Azuro/CEX API loops, signal bot, digital product sales.
Does **not** count: manual bounty submit, freelance, salary.

## Active lanes (priority)

1. **A1 Azuro** — paper 7 days first; rules in `agent/memory/lessons/azuro_paper_rules.md`
2. **A2/A3** — CEX scan or Telegram signals (pick one secondary)
3. **A5** — affiliate blog (background, 1 post/week max)

## Paper-trade rules (Azuro)

- Min edge vs model: document in daily log
- Skip if liquidity below floor or odds drift > threshold
- Log: count, USD exposure, by venue — 7 consecutive days before live go/no-go

## Finance JSON (parser expects English)

```json
{"market_id": "...", "side": "buy", "size_usd": 25, "reason": "..."}
```

## Kill criteria

- Paper expectancy ≤ 0 after 7 days → pivot to A3 + A4
- Never enable live without user Telegram approval

## Validation

- Append stats to `## Финансы` in daily log
- Update income_backlog `[x]` when task complete
- Propose capital change only in `## Итог`, not in code
