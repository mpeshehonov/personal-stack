# Job Hunt Backlog — Agent-Pickable Tasks

Aligned with `docs/superpowers/specs/2026-06-13-job-hunt-autopilot-design.md`.  
Pick **at most 1 job-hunt task per day** (after site health).

## Phase 0 — Discovery + digest (no auto-apply)

- [x] **JH-01** SQLite tables `job_leads`, `job_applications` in `orchestrator/state.py`
- [x] **JH-02** `job_hunt/scanner.py` — HH.ru fetch + dedup by external_id
- [x] **JH-03** `job_hunt/matcher.py` — score vs `site/content/resume/resume.json`
- [x] **JH-04** Wire `daily_job_scan()` into `orchestrator/main.py` + daily report section
- [x] **JH-05** Telegram `/jobs` command (Rich list of new leads)
- [x] **JH-06** `secrets/.env.jobhunt.template` + config loader

## Phase 1 — Draft + approve

- [x] **JH-07** `job_hunt/drafter.py` — cover letter template (RU, no hallucinations)
- [ ] **JH-08** `/approve apply <id>` and `/reject apply <id>` handlers
- [ ] **JH-09** Notify top-3 matches in daily Rich report

## Phase 2 — Resume sync

- [x] **JH-12** `resume_source.py` + `resume_sync.py` + digest (`hh_digest.py`)
- [x] **JH-13** Telegram `/jobs auth`, `/jobs sync`, `/jobs hh-digest`
- [x] **JH-13b** `docs/JOB-HUNT-AUTH-SETUP.md` + `scripts/check-job-hunt-auth.py`
- [x] **JH-13c** Document HH applicant API closure (`lessons/hh_applicant_api_closed.md`)
- [ ] **JH-14** Habr Career profile push (Playwright + session cookie)
- [ ] **JH-16** HH.ru browser RPA — apply + resume (Playwright; see `agent/memory/research/job_automation_rpa_2026.md`)
- [ ] **JH-17** HH resume edit + «поднять» via browser (or @hh_rabota_bot lift)
- [ ] **JH-18** RU IP / CDP to user desktop browser (anti-detect)
- [ ] **JH-19** Spike: official @hh_rabota_bot for resume lift only
- [ ] **JH-15** HH experience blocks in digest (full export from resume-data.ts)
- [ ] **JH-11** Application status tracking + weekly summary
- [x] ~~**JH-10** HH OAuth~~ — **cancelled** (API closed 2025-12-15)

## Rules

1. Never submit application without explicit `/approve apply`
2. Never push resume without `/approve resume` (unless `JOBHUNT_RESUME_AUTO_SYNC=true`)
3. **Do not configure HH OAuth** — applicant API closed
4. Never invent experience not in resume.json / resume-data.ts
5. Job hunt does not override site down or security fixes
