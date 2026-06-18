# Agent Harness Map

> Provider-neutral control plane for `/opt/personal-stack`. Last reviewed: 2026-06-15.

## Role

The **harness** (orchestrator + validators + policies) executes; the **model** proposes. Never rely on prompt-only safety for financial, external, or destructive actions.

## Core loop

```text
context pack → plan (1 item max per lane) → execute with tools → validate → daily log → commit memory
```

## Instruction hierarchy

| Layer | Path | When loaded |
|-------|------|-------------|
| Map | `agent/instructions.md` | Always (this file) |
| Daily task | `agent/tasks/daily_prompt.md` | Daily cycle |
| Income | `agent/memory/income_plan.md` | Daily + income tasks |
| Site backlog | `agent/tasks/site_backlog.md` | Daily |
| Bounty | `agent/tasks/bounty_*_prompt.md` | Bounty scanner only |
| Skills | `agent/skills/*/SKILL.md` | site-design for `site/`, income/bounty for earning |

## Autonomy matrix

| Lane | Autonomy | Approval gate |
|------|----------|---------------|
| Site fixes | draft → deploy script | auto if health OK |
| Finance live | proposal only | `FINANCE_LIVE=true` + user |
| Bounty submit | draft only | `/approve bounty` |
| Job apply | draft only | `/approve apply` |
| External send | blocked | human |

## Planning mode (daily)

Before edits, produce a **short plan artifact** in today's daily log under `## План`:

- objective (1 sentence)
- scope included / excluded
- validation (how to prove done)
- done condition

Max **1 site item + 1 income item** per cycle. Bug bounty research is orchestrator-only — do not duplicate hunt.

## Checkpoints

1. Health gathered — site OK or redeploy attempted
2. Plan written in daily log
3. At most one bounded change per lane executed
4. Validators pass (`daily_validator.py` sections present)
5. Lessons captured if failure repeated

## Source of truth

- PnL / goals: `agent/state.sqlite`, `finance_log`
- Income strategy: `agent/memory/income_plan.md`
- Pickable tasks: `agent/tasks/income_backlog.md`, `site_backlog.md`
- Bounty queue: SQLite `bounty_drafts`

## Skills (progressive disclosure)

- `agent/skills/income-harness/` — M1 lanes, paper rules
- `agent/skills/bounty-harness/` — semi-auto bounty
- `agent/skills/bounty-shopify/` — Shopify dev stores + Admin API hunt
- `agent/skills/site-design/` — **обязательно** перед правками `site/`

## Non-goals (daily agent)

- No `FINANCE_LIVE` without explicit user message
- No bounty submit / HackerOne API
- No secrets in logs or commits
- No multi-file refactors when light_mode=true
