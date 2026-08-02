# Agent Harness Map

> Provider-neutral control plane for `/opt/personal-stack`. Last reviewed: 2026-07-20.

## Role

The **harness** (orchestrator + validators + policies) executes; the **model** proposes. Never rely on prompt-only safety for external or destructive actions.

## Core loop

```text
context pack → plan (career focus) → execute with tools → validate → daily log → commit memory
```

## Instruction hierarchy

| Layer | Path | When loaded |
|-------|------|-------------|
| Map | `agent/instructions.md` | Always (this file) |
| Daily task | `agent/tasks/daily_prompt.md` | Daily cycle |
| Job hunt | `agent/tasks/job_hunt_backlog.md` | Daily |
| Career | `docs/career-growth-*.md` | Daily excerpt |
| Site backlog | `agent/tasks/site_backlog.md` | Emergency only |
| Skills | `agent/skills/*/SKILL.md` | resume-copy, cover-letter |

## Autonomy matrix

| Lane | Autonomy | Approval gate |
|------|----------|---------------|
| Site fixes | draft → deploy script | auto if health OK |
| Job scan | orchestrator daily | read-only |
| Job feedback | Telegram like/dislike | human |
| Source seed | propose in daily | `/approve source` |
| Cover draft | `/cover <id\|url\|текст> [hh\|tg\|email]` | human send; skill `cover-letter` |
| Job apply | draft only | human (future `/approve apply`) |
| Bounty / finance | **paused** | — |

## Planning mode (daily)

Before edits, produce a **short plan artifact** in today's daily log under `## План`:

- Objective / Included / Excluded / Validation / Done when

## Non-goals (paused)

- Autonomous crypto income, live trading, bounty hunt as primary
- Gumroad / PayPal / Stripe funnels
- Autonomous site redesign

## Related

- Goals: `agent/memory/goals.md`
- INDEX: `agent/memory/INDEX.md`
- Career hunter: `agent/job_hunt/`
