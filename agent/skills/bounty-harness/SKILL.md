---
name: bounty-harness
description: Semi-auto white-hat pentest — multi-phase research, submit-ready drafts, crypto payout platforms. Orchestrator owns hunt; daily extends catalog.
---

# Bounty Harness

**Primary income lane** until crypto wallet is funded (2026-06-23 pivot).

Daily agent: **do not** run deep hunt — `bounty/scanner.py` owns that. Pick tasks from `agent/tasks/bounty_backlog.md`.

## Pipeline (orchestrator)

```text
purge → scope → recon → hunt → report → validate → reviewer → pending draft
```

Cache: `agent/bounty/research_cache/<team>/`

## Platform strategy

- Catalog: `agent/memory/bounty_platforms.md` — **extend weekly**
- Curated rotation: `agent/bounty/programs.py`
- **Prefer crypto payout:** Immunefi, HackenProof, HackerOne (if crypto enabled on account)
- **Avoid:** GHSA/CVE template spam (purge queue)

Shopify dev stores: `agent/skills/bounty-shopify/SKILL.md`; credentials from `secrets/.env.bounty`.

## User gates

- Submit-ready draft → `/approve bounty <id>` or `/reject bounty <id>`
- Leads (`[Lead]`) — research notes, not auto-submit

## Daily agent role

- ≤1 item from `bounty_backlog.md` (add programs, payout docs, submit stubs)
- Summarize orchestrator outcome in `## Баг-баунти` (1–3 sentences)
- Remind user if pending drafts exist
- Do **not** duplicate research or purge queue

## Payout → wallet

When bounty pays out, log via `python3 -m finance.bounty_payout --net-usd <net> --platform <platform> --report-id <id>`. Target: same wallet as `YOUR_WALLET_ADDRESS` in finance env.
