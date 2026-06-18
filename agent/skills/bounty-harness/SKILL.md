---
name: bounty-harness
description: Semi-auto bug bounty — multi-phase research, submit-ready drafts only, no GHSA/CVE spam. Use when reviewing bounty daily summary, not for running hunt (orchestrator owns hunt).
---

# Bounty Harness

Daily agent: **do not** run deep hunt — `bounty/scanner.py` owns that.

## Pipeline (orchestrator)

```text
purge → scope → recon → hunt → report → validate → reviewer → pending draft
```

Cache: `agent/bounty/research_cache/<team>/`

Shopify with dev stores: load `agent/skills/bounty-shopify/SKILL.md`; credentials from `secrets/.env.bounty` (`SHOPIFY_SHOP*_DOMAIN`, `SHOPIFY_SHOP*_ADMIN_TOKEN`).

## User gates

- Submit-ready draft → `/approve bounty <id>` or `/reject bounty <id>`
- Leads (`[Lead]`) — research notes, not auto-submit

## Daily agent role

- Summarize bounty cycle outcome in `## Баг-баунти` (1–3 sentences)
- If pending drafts exist, remind user to review
- Do not duplicate research or purge queue
