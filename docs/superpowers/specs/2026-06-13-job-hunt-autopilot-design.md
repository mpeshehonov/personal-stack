# Job Hunt Autopilot — Design Spec

**Date:** 2026-06-13  
**Lane:** A9 (semi-autonomous, M2/M3 for $; M1 excluded — requires user approve)  
**Owner:** personal-stack agent

## Problem

Resume site alone is passive. User wants autonomous job search: discovery → tailored apply → tracking, without spam or ToS violations.

## Goals

1. Surface **high-match** vacancies daily (RU + remote frontend/fullstack).
2. Generate **draft** cover letter + resume bullet tweaks per vacancy.
3. User approves via Telegram before any external action.
4. Track pipeline in SQLite; show in `/jobs` and daily report.

## Non-goals

- Fully unattended mass applications (legal/reputation risk).
- LinkedIn scraping without official API.
- Fake experience or LLM hallucinated employers.

## Architecture

```
job_hunt/
  scanner.py      # fetch HH.ru API, optional Habr RSS
  matcher.py      # score vs resume.json skills + title keywords
  drafter.py      # cover letter + talking points (cursor or template)
  store.py        # CRUD job_leads, job_applications
  digest.py       # format for Telegram Rich Message

orchestrator/main.py  # daily_bounty_scan pattern → daily_job_scan()
telegram_bot/bot.py   # /jobs, /approve apply <id>, /reject apply <id>
```

## Data model

**job_leads**
- id, ts, source (hh|habr|manual), external_id, url, title, company
- salary_raw, location, skills_json, description_snippet
- match_score (0–100), match_reasons_json, status (new|approved|rejected|applied)

**job_applications**
- id, lead_id, ts, cover_letter, resume_variant_path (optional)
- status (draft|sent|viewed|rejected|interview), notes

## Matching rules (v1)

| Signal | Weight |
|--------|--------|
| Title contains Senior/Lead Frontend/React/Next | +25 |
| Skills overlap with resume.json | +5 each, max 40 |
| Remote / hybrid | +10 |
| Salary min ≥ threshold (env) | +10 |
| Staffing agency / mass hiring spam keywords | −30 |

Threshold for digest: **match_score ≥ 55**.

## HH.ru integration (v1)

- Public API: `https://api.hh.ru/vacancies?text=frontend&area=113&schedule=remote`
- Rate limit: 1 req / 2s, User-Agent with contact email
- Store `external_id` for dedup

> **Update 2025-12-15:** Applicant API (OAuth, resume edit, apply) **closed**. Vacancy search may still work without token. Resume sync → `/jobs hh-digest` (manual) or JH-16 Playwright. See `agent/memory/lessons/hh_applicant_api_closed.md`.

## Telegram UX

```
/jobs              — top 10 new leads (Rich table)
/approve apply 42  — mark approved, generate final cover letter
/reject apply 42   — dismiss
```

Daily cycle appends **Job Hunt** section: N new, top 3 titles + scores.

## Approve → apply flow (Phase 1)

1. User `/approve apply 42`
2. Agent prepares: cover letter MD, link to vacancy
3. **Manual step v1:** bot sends deep link + copy-paste blocks (HH often needs captcha)
4. ~~**Phase 2:** HH OAuth~~ — cancelled (applicant API closed 2025-12-15)

## Env

```bash
# secrets/.env.jobhunt
JOBHUNT_ENABLED=true
JOBHUNT_HH_TEXT="frontend react typescript"
JOBHUNT_MIN_MATCH=55
JOBHUNT_MIN_SALARY_RUB=250000
JOBHUNT_USER_AGENT="personal-stack-agent/1.0 (kassady71@gmail.com)"
```

## Risks

| Risk | Mitigation |
|------|------------|
| Low-quality spam applies | approve gate + match threshold |
| Stale vacancies | re-fetch skips known external_id |
| LLM inventing skills | drafter only uses resume.json + vacancy text |

## Implementation order

1. `store.py` + migrations in `state.py`
2. `scanner.py` + `matcher.py` + unit-less smoke test
3. `/jobs` command + daily digest
4. `drafter.py` + approve flow
5. Backlog item JH-05: Habr RSS optional

## Related

- `agent/memory/income_plan.md` — A8 freelance funnel (this automates inbound half)
- `agent/tasks/job_hunt_backlog.md` — pickable tasks
