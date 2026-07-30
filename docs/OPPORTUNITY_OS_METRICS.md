# Opportunity OS Metrics

Definitions for measurable quality. **Do not claim improvement without data.**

## Counters (per scan / day)

| Metric | Meaning |
|--------|---------|
| `source_count` | Active rows in `job_sources` |
| `raw_signals` | Vacancies fetched before filters |
| `deduplicated` | skipped_existing + skipped_duplicates |
| `filtered` | below Stage A `JOBHUNT_MIN_MATCH` |
| `scored` | new `job_leads` / opportunities created |
| `shown_to_user` | JOB opportunities currently in DB (proxy until explicit impressions) |
| `liked` / `saved` / `applied` / `interview` / `offer` | From `opportunity_feedback` |

## Rates

| Metric | Formula | Null when |
|--------|---------|-----------|
| `precision_at_5` | positive feedback on judged top-5 new / judged top-5 | no feedback on top-5 |
| `apply_rate` | APPLY / (LIKE+SAVE) | no likes |
| `interview_rate` | INTERVIEW / APPLY | no applies |
| `feedback_coverage` | feedback events / shown | shown=0 |
| `source_quality` | weight + enabled per source | — |

## Storage

- Daily snapshot: `opportunity_metrics_daily` in `agent/state.sqlite`
- Compute: `opportunity.metrics.compute_metrics(scan_summary)`

## Hirify caveat

Dislikes with reason `paywall` (default for Hirify «Мимо») **do not** lower source weight.  
Track actionability separately via `probability` score and `analysis.paywall`.

## Insufficient data flag

`insufficient_data=true` while `precision_at_5` or `apply_rate` is null.  
Orchestrator / brief must not say «стало лучше» in that state.
