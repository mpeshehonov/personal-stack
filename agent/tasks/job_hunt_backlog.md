# Job Hunt Backlog — Career Hunter

Aligned with `docs/career-growth-system.md` and vacancy autopilot.
Pick **at most 1–2 job-hunt tasks per day** (after site health).
**Do not** pick income/bounty tasks.

## Phase 0 — Discovery + digest (done)

- [x] **JH-01** SQLite tables `job_leads`, `job_applications`
- [x] **JH-02** Multi-source scanner
- [x] **JH-03** Matcher vs resume
- [x] **JH-04** Daily scan + report
- [x] **JH-05** Telegram `/jobs`
- [x] **JH-06** `.env.jobhunt.template`

## Phase 1 — Career hunter v1 (2026-07-20)

- [x] **JH-20** Senior Product/FE matcher bar + min_match 70 + spam bans
- [x] **JH-21** `job_sources` + `job_feedback` + weight learning
- [x] **JH-22** `/jobs like|dislike`, `/sources`, `/approve source`
- [x] **JH-23** Flip daily north star off income/bounty
- [ ] **JH-08** `/approve apply <id>` and `/reject apply <id>`
- [ ] **JH-09** Notify top matches more aggressively (optional TG push outside daily)
- [ ] **JH-24** Propose new TG channels in daily (seed → `/approve source`)
- [ ] **JH-11** Application status tracking + weekly summary

## Phase 2 — Resume sync / RPA

- [x] **JH-12..JH-13c** digest + auth docs
- [ ] **JH-14** Habr Career profile push
- [ ] **JH-16** HH browser RPA
- [ ] **JH-15** HH experience blocks in digest
- [x] ~~**JH-10** HH OAuth~~ — cancelled (API closed)

## Rules

1. Never submit application without explicit human send (future `/approve apply`)
2. Never push resume without `/approve resume`
3. **Do not configure HH OAuth**
4. Never invent experience not in resume sources
5. Job hunt does not override site down
6. TG messages: plain text, short dashes — no decorative arrows/emoji bullets
