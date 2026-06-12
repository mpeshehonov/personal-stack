# Roadmap Q3 2026 — personal-stack

Цель: выйти из состояния «инфраструктура есть, продукт сырой» на три фронта параллельно.

## Текущий уровень

| Фронт | Сейчас | Цель |
|-------|--------|------|
| Сайт | ~3/10 визитка | **8/10** — portfolio + case studies + blog + conversion |
| Income (M1) | paper-only, backlog не закрыт | Phase 0 validation + daily scan в прод |
| Job hunt | не существует | semi-auto pipeline с approve-flow |

## Параллельные потоки

### Stream A — Site 8/10 (`agent/tasks/site_backlog.md`)

**North star:** HR и hiring manager за 30 секунд понимают уровень, домены и impact; есть повод написать в Telegram.

Milestone A1 (эта неделя):
- Homepage: hero + selected work + experience preview + CTA
- `/projects` — 3–5 кейсов с stack, role, impact
- `/blog` — MDX, первый пост-скелет
- Visual polish: typography scale, section rhythm, micro-interactions

Milestone A2:
- OG images, theme toggle, analytics-free counter
- PDF/resume sync with site content single source

### Stream B — Income Phase 0 (`agent/tasks/income_backlog.md`)

**North star:** M1 $1k autonomous к 2026-09-30 через Azuro paper + CEX scan.

This week:
- IB-01: multi-venue scan in daily cycle, log to daily report
- IB-02: `azuro_paper_rules.md`
- IB-05 prep: `finance/signal_rules.py` filter skeleton

### Stream C — Job Hunt Autopilot (`agent/tasks/job_hunt_backlog.md`)

**North star:** агент находит релевантные вакансии, готовит отклик, ты только `/approve apply <id>`.

Design: `docs/superpowers/specs/2026-06-13-job-hunt-autopilot-design.md`

Phase 0 (no auto-submit):
- SQLite `job_applications` + `job_leads`
- HH.ru public API / RSS parser (read-only)
- Match score vs `resume.json` skills
- Draft cover letter in Russian
- Daily digest in Telegram + `/jobs` command

Phase 1 (semi-auto):
- User approves → agent fills form / sends via API where allowed
- Track status: sent → viewed → interview

**NOT in scope:** mass spam, ToS-violating bots on LinkedIn without API.

## Daily agent priority (updated)

1. Health
2. Site — max 1 item from site_backlog
3. Income — max 1 from income_backlog
4. Job hunt — max 1 from job_hunt_backlog (after Phase 0 scaffold)
5. Bounty draft
6. Memory writeback

## Success metrics (4 weeks)

- Site: Lighthouse perf ≥90, 3 case studies live, 1 blog post
- Income: 7 days paper logged, go/no-go doc
- Jobs: ≥5 scored leads/week in Telegram digest
