# Opportunity OS — Implementation Report (2026-07-30)

## What changed

Personal-stack gained an **Opportunity Core** (`agent/opportunity/`) with Jobs as the first vertical. Existing `job_hunt` collectors, matcher (Stage A), SQLite `job_leads`, and Telegram job cards remain. Opportunities are a dual-write overlay with multi-factor scores, next actions, brief, and feedback that no longer punishes Hirify for paywall skips.

## Reused

- Collectors: HH, Habr, Hirify, HireHi, Telegram
- `matcher.score_vacancy` → Stage A filter
- `dedup.py`, `scanner.scan_and_store_leads`, `daily_job_scan`
- `job_leads` / `job_sources` / `job_feedback` / `job_applications`
- Telegram cards Ок/Мимо/Сопровод + `/jobs`
- Daily orchestrator cycle

## New modules

| Module | Role |
|--------|------|
| `opportunity/models.py` | Types, statuses, feedback, score shapes |
| `opportunity/profile.py` | Versioned profile (`agent/memory/opportunity_profile.json`) |
| `opportunity/scoring.py` | Stage A wrapper + Stage B components + overall |
| `opportunity/repository.py` | `opportunities`, `opportunity_feedback`, metrics table |
| `opportunity/migrate.py` | Backfill leads + Hirify repair |
| `opportunity/feedback.py` | Opp feedback; paywall ≠ source penalty |
| `opportunity/actions.py` | Next-action engine |
| `opportunity/preferences.py` | Explainable slow preference model |
| `opportunity/brief.py` | Daily Opportunity Brief |
| `opportunity/metrics.py` | Funnel + rates |
| `opportunity/ideas.py` | Strategic non-job ideas (switch/niche/contract) |
| `opportunity/services.py` | Upsert from lead + after-scan hook |

## Migrations

1. Schema: `opportunities`, `opportunity_feedback`, `opportunity_metrics_daily` (via `init_db` / `ensure_opportunity_schema`)
2. Backfill: all `job_leads` → JOB opportunities (idempotent)
3. Hirify: re-enable + floor weight ≥ 1.2 if disabled by past paywall dislikes
4. Profile: seed from resume + career-copy defaults

Data loss: **none** — `job_leads` untouched.

## Scoring

- **Stage A:** existing matcher; persist if ≥ `JOBHUNT_MIN_MATCH`
- **Stage B:** `fit`, `income`, `growth`, `probability`, `strategic`, `urgency` (0–100 + reasons)
- **overall_score:** deterministic weighted average from profile weights
- Hirify: lower `probability` / paywall flag; next action often `RESEARCH_COMPANY`
- Vacancy age via `_published_at` when present

## Feedback rules (Hirify fix)

- Hirify «Мимо» without note → reason `paywall` → **source weight unchanged**
- Explicit `/jobs dislike <id> bad_fit` → source weight decreases
- Opportunity feedback actions: LIKE, DISLIKE, SAVE, APPLY, SKIP, NOT_RELEVANT, INTERVIEW, OFFER, REJECTED, HIRED

## How to run

```bash
# Local tests
cd /path/to/personal-stack
STACK_DIR=$PWD PYTHONPATH=agent python3 -m unittest agent.tests.test_opportunity_os -v

# Migrate existing DB on VPS (also runs on scan/brief)
STACK_DIR=/opt/personal-stack PYTHONPATH=/opt/personal-stack/agent \
  python3 -c "from opportunity.migrate import migrate_opportunity_core; print(migrate_opportunity_core())"

# Telegram
/brief
/profile
/profile set remote_preference=remote_only
/jobs dislike 12 paywall
/jobs dislike 12 bad_fit
```

After deploy: `sudo systemctl restart telegram-bot agent-orchestrator`

## Telegram commands

| Command | Purpose |
|---------|---------|
| `/brief` | Top opportunities + today’s actions + funnel + idea |
| `/profile` | Show editable opportunity profile |
| `/profile set k=v` | Patch scalar profile fields |
| `/jobs` … | Unchanged cards; Hirify Мимо preserves source |

Menu: added **Brief**.

## Metrics without data yet

Until feedback accumulates: `precision_at_5`, `apply_rate`, `interview_rate` may be null → `insufficient_data=true`. See `docs/OPPORTUNITY_OS_METRICS.md`.

## Remaining — Clients

- Collectors for inbound/outbound client leads
- Separate scoring weights (retainer vs FT)
- CRM status machine beyond JOB

## Remaining — Products

- Productize portfolio niches (seat-map, KKM, sendonate patterns) as PRODUCT opportunities with outreach drafts
- Evidence links (no invented metrics)

## Remaining — Network

- Person/Company tables from `career-opportunities-schema.md`
- Warm intro / LinkedIn outreach tracking
- `/brief` section for network follow-ups

## Improvement backlog (scoring / search)

1. Employer memory after dislike (cross-board suppress)
2. Explicit impressions log for true precision@5
3. Hirify: enrich with original board URL when API exposes it → higher actionability
4. Expand `ideas.py` with weekly Cursor-assisted research (still human-approved)
5. Separate source_relevance_weight vs actionability_score in `job_sources.stats_json`

## Docs

- Audit: `docs/OPPORTUNITY_OS_AUDIT.md`
- Plan: `docs/superpowers/plans/2026-07-30-opportunity-os.md`
- Metrics: `docs/OPPORTUNITY_OS_METRICS.md`
