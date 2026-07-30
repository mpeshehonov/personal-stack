# Opportunity OS Implementation Plan (2026-07-30)

> Using writing-plans skill. Jobs-first vertical; no microservices.

## Goal

Add `agent/opportunity/` as Opportunity Core; dual-write from `job_hunt`; Stage A = existing matcher; Stage B = multi-factor scores; Telegram brief; tests + metrics docs.

## Files

| Path | Responsibility |
|------|----------------|
| `agent/opportunity/models.py` | Enums + dataclasses |
| `agent/opportunity/profile.py` | Versioned profile JSON load/save |
| `agent/memory/opportunity_profile.json` | Editable profile seed |
| `agent/opportunity/scoring.py` | Stage A wrapper + Stage B components + overall |
| `agent/opportunity/repository.py` | SQLite CRUD for opportunities / feedback / metrics |
| `agent/opportunity/migrate.py` | Schema + backfill from job_leads; Hirify repair |
| `agent/opportunity/feedback.py` | Opportunity feedback + gated source weight |
| `agent/opportunity/actions.py` | Next-action engine |
| `agent/opportunity/preferences.py` | Explainable preference adjustments |
| `agent/opportunity/brief.py` | Daily brief text |
| `agent/opportunity/metrics.py` | Funnel counters + rates |
| `agent/opportunity/ideas.py` | Non-vacancy strategic ideas (switch/niche) |
| `agent/opportunity/services.py` | Upsert from lead, rescore, brief pipeline |
| `orchestrator/state.py` | Call migrate on init_db |
| `job_hunt/scanner.py` | Dual-write after add_job_lead |
| `job_hunt/hirify.py` | Pass published_at / actionability hints |
| `job_hunt/sources.py` | Route feedback through opportunity layer |
| `telegram_bot/bot.py` + `jobs_ui.py` | `/brief`, optional callbacks |
| `orchestrator/main.py` / daily_report | Attach brief snippet |
| `agent/tests/opportunity/*` | Unit tests |
| `docs/OPPORTUNITY_OS_METRICS.md` | Metrics definitions |
| `docs/OPPORTUNITY_OS_IMPLEMENTATION.md` | Final report |

## Tasks

1. Models + profile + schema migrate (backfill leads)
2. Scoring Stage B + Hirify actionability/staleness
3. Feedback + preferences + next actions
4. Wire scanner dual-write + sources feedback gate
5. Brief + Telegram + daily report
6. Metrics, tests, docs
7. Run tests

## Done when

- Existing job_leads intact and backfilled
- `/brief` works
- Paywall dislike does not disable Hirify
- Tests pass without live network
- LLM not required for pipeline
