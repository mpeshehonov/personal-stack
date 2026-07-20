# Career Growth Backlog

**Related:** `docs/career-growth-system.md`, `docs/career-opportunities-schema.md`  
**Rule:** each task must move a KPI (companies scored, outreaches, replies, interviews, income).  
**Deprioritized lanes:** crypto trading, bounty-as-primary, Gumroad — not in this backlog.

Complexity: **S** ≤0.5d · **M** 1–3d · **L** 1–2w · **XL** >2w

---

## P0 — Do immediately (this week)

### CG-01 — Flip agent north star to career
- **Why:** Daily Cursor/attention still burns on bounty/finance; career is the bottleneck.  
- **Result:** `daily_prompt.md`, `goals.md`, `INDEX.md`, context pack prioritize career; bounty/finance background.  
- **Complexity:** S  
- **Depends on:** —  
- **KPI:** career tasks completed / week; Cursor hours on career ≥70%

### CG-02 — Lock positioning copy v1
- **Why:** Without a sharp profile, outreach and site contradict.  
- **Result:** Approved one-liner + primary title **Senior Product Engineer (Frontend-leaning)**; secondary A–D summaries drafted in `career-copy-notes` or resume overlay.  
- **Complexity:** S  
- **Depends on:** your review of wording  
- **KPI:** consistent title across site/PDF/outreach

### CG-03 — Resume master pass (no fiction)
- **Why:** Intl/CTO packaging is weak; ASAP + skills laundry list hurt.  
- **Result:** Updated `resume.json` / `resume-data.ts` / EN: title, summary, trimmed skills, flagship-first; list TODOs for metrics you must confirm.  
- **Complexity:** M  
- **Depends on:** CG-02; your metrics answers  
- **KPI:** PDF ready for founder/CTO send

### CG-04 — Project taxonomy on site (compress)
- **Why:** 31 projects dilute X5/BI.ZONE/NLMK/Citilink/POTALONU.  
- **Result:** Featured ≤6; archive Bitrix-era & fragments; `/projects` readable.  
- **Complexity:** M  
- **Depends on:** CG-02  
- **KPI:** homepage clarity; fewer bounce to noise

### CG-05 — Schema + SQLite tables for Company/Evidence
- **Why:** Cannot score/CRM without entities.  
- **Result:** Implement core tables from schema (Company, Evidence, ResearchTask minimum); migrations in `state.py`.  
- **Complexity:** M  
- **Depends on:** schema doc approval  
- **KPI:** ≥1 company row with evidence

### CG-06 — Seed 30 companies (manual + adapters)
- **Why:** Need deal flow now, not perfect automation.  
- **Result:** ANY.RUN, Rogii + 28 similar with `source_urls`; initial scores.  
- **Complexity:** M  
- **Depends on:** CG-05  
- **KPI:** 30 scored companies

### CG-07 — Telegram shortlist UX
- **Why:** You operate via TG; must review/approve without DB CLI.  
- **Result:** `/companies`, `/company <id>`, `/approve company`, `/reject company`.  
- **Complexity:** M  
- **Depends on:** CG-05  
- **KPI:** daily review habit

### CG-08 — First 10 outreach drafts (human send)
- **Why:** Money comes from conversations, not infra.  
- **Result:** 10 personalized drafts for shortlist; you send manually; tracked as Outreach `sent`.  
- **Complexity:** M  
- **Depends on:** CG-02, CG-06, CG-07  
- **KPI:** 10 sent; reply rate logged

---

## P1 — Within a month

### CG-09 — Person + brief pipeline
- **Why:** Hiring happens via people.  
- **Result:** Person/Contact tables; `/brief`; research brief template; `/approve contact`.  
- **Complexity:** L  
- **Depends on:** CG-05–07  
- **KPI:** briefs for top 15 companies

### CG-10 — Outreach approve flow
- **Why:** Level 3–4 automation with safety.  
- **Result:** Outreach entity + `/approve outreach`; reminders D+3/D+7.  
- **Complexity:** M  
- **Depends on:** CG-09  
- **KPI:** follow-up compliance; reply rate

### CG-11 — Vacancy adapters → Company seeds
- **Why:** Reuse existing scanners as discovery feed.  
- **Result:** Employer extraction from HH/Habr/Hirify/HireHi/TG → upsert Company.  
- **Complexity:** M  
- **Depends on:** CG-05  
- **KPI:** auto seed rate / week

### CG-12 — Explainable scoring v1 in code
- **Why:** Shortlist must be auditable.  
- **Result:** `scoring.py` with weights + evidence IDs; shown in TG.  
- **Complexity:** M  
- **Depends on:** CG-05  
- **KPI:** shortlist precision (your thumbs-up %)

### CG-13 — Site hero + dual CTA
- **Why:** Job-seeker vs client conflict.  
- **Result:** Hero/ContactCTA split for hiring managers vs founders/clients; EN ASAP softened.  
- **Complexity:** M  
- **Depends on:** CG-02  
- **KPI:** inbound TG quality

### CG-14 — 4 flagship case study pages
- **Why:** CTO/clients need depth.  
- **Result:** `/projects/[slug]` for 4 flagships (problem → decisions → outcome).  
- **Complexity:** L  
- **Depends on:** CG-04  
- **KPI:** time-on-page; outbound link usage in outreach

### CG-15 — ResumeVersion overlays A/B
- **Why:** One master, targeted packaging.  
- **Result:** Versions for enterprise FE vs fullstack ownership; export paths.  
- **Complexity:** M  
- **Depends on:** CG-03  
- **KPI:** tailored sends

### CG-16 — Wire `/approve apply` for legacy vacancy path
- **Why:** Finish half-built job loop for open roles.  
- **Result:** Status machine + deep link / paste checklist (not silent submit).  
- **Complexity:** M  
- **Depends on:** existing JH-08  
- **KPI:** applications tracked >0

### CG-17 — Daily report «Карьера» section
- **Why:** Visibility of pipeline.  
- **Result:** Top companies, outreaches due, KPI snapshot; finance weekly.  
- **Complexity:** S  
- **Depends on:** CG-01, CG-05  
- **KPI:** awareness / action rate

### CG-18 — Compensation & constraints interview (with you)
- **Why:** Unknowns block targeting.  
- **Result:** Written floor (USD/₽), entity preferences, English interview readiness, geo constraints.  
- **Complexity:** S  
- **Depends on:** you  
- **KPI:** better company filters  
- **Status:** DONE 2026-07-20 — target $3–4k/mo; rails: самозанятый / ТК РФ / USDT; Playwright OK; job ASAP priority

### CG-03b — Surgical resume upgrade (anti-slop)
- **Why:** Resume reads mid due to titles/verbs/skills, not empty experience; full rewrite risks AI slop.  
- **Result:** One master RU profile: Senior Product Engineer; strong verbs; trimmed skills; tighter bullets; no invented metrics; synced to `resume-data.ts` + `resume.md` + `resume.json` + HH digest.  
- **Complexity:** M  
- **Depends on:** CG-02 (done in principle); your OK to edit  
- **KPI:** same text usable on site / HH / Habr / LinkedIn without per-platform rewrite

---

## P2 — After hypothesis confirmation

*Hypothesis:* CIS-connected intl product companies + personalized founder/CTO outreach → interviews/contracts within 90 days.

### CG-19 — Enrichment adapters (careers page, GH org stack)
- **Why:** Scale research.  
- **Complexity:** L  
- **Depends on:** P1 working; ≥5 replies  
- **KPI:** enrichment coverage %

### CG-20 — Wellfound / YC directory seed packs
- **Why:** More intl startups.  
- **Complexity:** M  
- **Depends on:** CG-11 pattern  
- **KPI:** new high-score companies / month

### CG-21 — AI-augmented Product Engineer packet (profile C)
- **Why:** Only if startups respond to velocity angle.  
- **Complexity:** M  
- **Depends on:** market signal from replies  
- **KPI:** conversion for profile C sends

### CG-22 — Product discovery interviews (own product)
- **Why:** Product lane only if validated.  
- **Result:** ≥5 problem interviews; go/no-go note.  
- **Complexity:** L  
- **Depends on:** not blocking employment/contract  
- **KPI:** validated problem or kill

### CG-23 — HH Playwright apply/resume (JH-16/17)
- **Why:** Optional volume on RU boards.  
- **Complexity:** XL  
- **Depends on:** **explicit risk accept**; RU IP/session strategy  
- **KPI:** applications/week without ban

### CG-24 — Habr profile push (JH-14)
- **Why:** RU visibility.  
- **Complexity:** L  
- **Depends on:** cookie + approve  
- **KPI:** Habr profile freshness

### CG-25 — Lightweight CRM dashboard on site (auth’d)
- **Why:** Only if TG UX insufficient.  
- **Complexity:** L  
- **Depends on:** P1 scale pain  
- **KPI:** time-to-review shortlist

---

## P3 — Do not do yet

| ID | Item | Why not now |
|----|------|-------------|
| CG-30 | Mass LinkedIn scraping / unattended InMail bots | ToS + ban + spam |
| CG-31 | Autonomous outreach send without approve | Reputation risk |
| CG-32 | Rewrite orchestrator from scratch | Existing harness OK |
| CG-33 | Bounty/finance as daily primary | Wrong bottleneck |
| CG-34 | Gumroad / MoR for RU | Already blocked |
| CG-35 | “Learn more React” training track | Not the bottleneck |
| CG-36 | Fake Staff/Principal title without evidence | Credibility risk |
| CG-37 | VPN resale as income | Deferred / ToS |
| CG-38 | Full ATS multi-board auto-apply farm | Low quality, high risk |
| CG-39 | Build new personal product before 5 interviews | Fantasy risk |

---

## Suggested implementation order (first 14 days)

```text
Day 1–2   CG-01, CG-02, CG-18 (async questions to you)
Day 3–5   CG-03, CG-04, CG-13
Day 5–8   CG-05, CG-06, CG-07
Day 9–14  CG-08, CG-12, CG-17
Then      CG-09 → CG-10 → CG-11 → CG-16
```

---

## KPI dashboard (track weekly in daily log)

| Metric | Target W4 | Target W12 |
|--------|-----------|------------|
| Companies scored | 30 | 100 |
| Shortlist | 10 | 40 |
| Outreaches sent | 10 | 40 |
| Reply rate | ≥20% | ≥20% |
| Conversations | 2 | 15 |
| Interviews / paid calls | 1 | 5 |
| Offers or signed contracts | 0–1 | 1–2 |
| Realized ₽/mo | rising | → 500k by M6 |

---

## Open questions for you (block precision)

1. Floor compensation for employment vs contract (USD and ₽)?  
2. English for live interviews — keep B1 public or raise claim?  
3. Accept Playwright HH ban risk? (yes/no)  
4. Metrics you can publish for X5 / BI.ZONE / NLMK / Citilink / POTALONU?  
5. Contract vehicle: ИП / foreign / crypto OK?  
6. Prefer employment, contract, or mix for the next 6 months?
