# Opportunity OS — Audit (2026-07-30)

Статус: audit complete → implementation follows.  
Scope: evolve `personal-stack` without rewrite; Jobs first vertical.

---

## 1. Current vacancy flow

```text
systemd daily.timer (06:00 UTC)
  → kv daily_trigger
  → orchestrator.run_daily_cycle
       → Cursor daily agent (memory log only; no vacancy scan)
       → job_hunt.scanner.daily_job_scan
            → fetch_all_vacancies (HH, Habr, Hirify, HireHi, TG)
            → dedupe_vacancies (URL + title|company fingerprint)
            → score_vacancy (matcher, 0–100)
            → if score ≥ JOBHUNT_MIN_MATCH (70): add_job_lead(status=new)
       → Telegram daily report (counts + top_leads)

Manual:
  /jobs scan → same scan_and_store_leads
  /jobs → cards of status=new
  Ок/Мимо/Сопровод → apply_feedback / drafter
```

Key entrypoints:

| Step | Module | Function |
|------|--------|----------|
| Collect | `job_hunt/scanner.py` | `fetch_all_vacancies` |
| Dedupe | `job_hunt/dedup.py` | `dedupe_vacancies`, `vacancy_fingerprint` |
| Score | `job_hunt/matcher.py` | `score_vacancy` |
| Persist | `orchestrator/state.py` | `add_job_lead` |
| Feedback | `job_hunt/sources.py` | `apply_feedback` |
| Cover | `job_hunt/drafter.py` | `draft_cover_letter` |
| TG UI | `telegram_bot/jobs_ui.py`, `bot.py` | cards + callbacks `j:*` |

---

## 2. Storage

| Store | Path / table | Role |
|-------|--------------|------|
| SQLite | `agent/state.sqlite` | primary CRM-lite |
| `job_leads` | leads + `match_score` + status | vacancy truth for collectors |
| `job_applications` | cover drafts | |
| `job_sources` | weight / enabled / stats | source learning |
| `job_feedback` | like/dislike/applied/interview | |
| `kv` | triggers, cursor agent ids, resume sync | |
| Resume | `site/content/resume/resume.json` | skills for matcher |
| Memory | `agent/memory/*` | ops, lessons, daily logs — not leads |

No separate repository layer: CRUD lives in `orchestrator/state.py`.

---

## 3. Lead model (today)

`job_leads`: `id, ts, source, external_id, url, title, company, salary_raw, location, skills_json, description_snippet, match_score, match_reasons_json, status`  
UNIQUE `(source, external_id)`.

Statuses: `new | liked | rejected | applied | interview`.

HH-like vacancy dict is the cross-source contract (`name`, `employer`, `snippet`, `_source`, …).

---

## 4. Scoring (today)

`matcher.score_vacancy`: keyword/rule score, baseline 40, clamp 0–100.

- Hard kill: junior/intern/стажёр (`HARD_SPAM` → 0)
- Weak mismatch without React → 5
- Senior title +20, middle −15, FE title +15, stack/resume overlap, remote/hybrid, salary, agency

**Not in score:** source weight, vacancy age, apply actionability (paywall), strategic career value.

Source weights gate **fetch**, not ranking. Dislike −0.25; weight &lt; 0.35 disables source.

---

## 5. Feedback (today)

Actions: `like`, `dislike`, `applied`, `interview`, `reject_reason`.

Effects: update `job_feedback` + lead status + **source weight only**.  
Does **not** re-score leads or learn feature preferences.

### Known bug (user, 2026-07-30)

Hirify often requires **Hirify Plus** to see contacts. User pressed «Мимо» on otherwise strong matches → source weight collapsed / disabled.  
Hirify remains the **best relevance source**; dislike was about **actionability**, not fit.  
System also ignored how long vacancies stay open.

---

## 6. Telegram interactions

- Reply menu: Вакансии / Скан / Источники / Понравилось / Справка
- Card buttons: Ок (`like`), Мимо (`dislike`), Сопровод, Открыть URL
- Commands: `/jobs`, `/sources`, `/cover`, `/approve source`, resume sync helpers
- Daily report: job section with new_count + top_leads — **volume-oriented**, not action-oriented

---

## 7. Reuse for Opportunity OS

| Keep as-is | Wrap / extend | Do not break |
|------------|---------------|--------------|
| All collectors + HH-like shape | Dual-write → `opportunities` | `job_leads` uniqueness |
| `score_vacancy` as Stage A filter | Stage B multi-factor scores | TG `j:*` callbacks |
| `dedupe_*`, URL exists | Preferential feature learning | `daily_job_scan` summary keys |
| `apply_feedback` source deltas | Split paywall vs fit dislike | resume sync / kv |
| `jobs_ui` cards | Brief + next-action buttons | systemd daily timer |
| `career-copy-notes` + resume.json | Seed editable opportunity profile | |

Design docs already exist (`career-opportunities-schema.md`, `career-growth-system.md`) — Opportunity Core is a **leaner Jobs-first** cut, not full Company/Person CRM yet.

---

## 8. Regression risks

1. Changing lead status enum without TG mapping.
2. Dropping `job_leads` or renaming summary keys in daily report.
3. Putting source weight into match_score without separating actionability.
4. Disabling Hirify again via paywall dislikes.
5. Breaking HH-like adapter fields before matcher.
6. Dual score confusion (match_score vs overall_score) in UI — surface both with labels.
7. Migrating SQLite without backfill → empty Opportunity brief.

**Mitigation:** dual-write + backfill; keep collectors writing `job_leads`; Opportunity is overlay; paywall feedback must not disable Hirify.

---

## 9. Target pipeline (Jobs vertical)

```text
Sources → Raw signals → Normalize (HH-like)
  → Stage A filter (existing matcher hard rules + min_match)
  → job_leads (compat)
  → opportunities (type=JOB)
  → Stage B personal scores (fit/income/growth/probability/strategic/urgency)
  → next_action + priority
  → Telegram Opportunity Brief
  → opportunity feedback (+ source feedback with reason gating)
  → preference model (explainable, slow updates)
```

Types `CLIENT | PRODUCT | NETWORK | OTHER` in schema only for v1.

---

## 10. Improvement ideas (beyond first ship)

1. **Actionability score** — can apply without paywall / has company / has contacts path.
2. **Freshness / staleness** — published_at age; demote stale posts.
3. **Employer memory** — after dislike, suppress same employer+role across boards (lesson already documents FP).
4. **Source quality ≠ apply quality** — separate relevance learning from actionability.
5. **Strategic ideas lane** — specialization switches (e.g. RN/Expo, Web3, seats.io-like niche), contract/retainers, productizing portfolio — as `OTHER`/`PRODUCT` opportunities generated from profile gaps, not vacancy scrape.
6. **Precision@5 tracking** — measure brief quality before claiming wins.
