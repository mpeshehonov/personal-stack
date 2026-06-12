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

- [ ] **JH-07** `job_hunt/drafter.py` — cover letter template (RU, no hallucinations)
- [ ] **JH-08** `/approve apply <id>` and `/reject apply <id>` handlers
- [ ] **JH-09** Notify top-3 matches in daily Rich report

## Phase 2 — Semi-auto apply (user OAuth)

- [ ] **JH-10** HH OAuth token storage in secrets (optional)
- [ ] **JH-11** Application status tracking + weekly summary

## Rules

1. Never submit application without explicit `/approve apply`
2. Never invent experience not in resume.json
3. Job hunt does not override site down or security fixes
