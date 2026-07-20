# Career Growth System — Strategy & Architecture

**Status:** iteration-1 in progress (career hunter runtime)  
**Date:** 2026-07-20  
**Owner:** Максим Пешехонов  
**Income goals:** autonomous crypto/bounty lanes **cancelled** — focus employment/contract deal flow  
**Primary lanes:** international remote employment · high-ticket freelance/contract · product (only if validated)

---

## 1. Current state

### What the stack is today

Self-hosted **ops + income harness** with a side lane for job hunt:

| Layer | Path | Reality |
|-------|------|---------|
| Site / resume | `site/` | Strong RU recruiter funnel (resume → PDF → Telegram) |
| Orchestrator | `agent/orchestrator/` | Daily cycle: health → Cursor agent → finance paper → bounty drafts → job scan |
| Job hunt | `agent/job_hunt/` | Vacancy-centric: multi-source scan → score → `/cover` draft |
| Telegram | `agent/telegram_bot/` | `/jobs`, `/cover`, `/approve resume|bounty` — **no `/approve apply`** |
| Memory | `agent/memory/` | Daily logs, goals, income/bounty-first |
| Finance / bounty | `agent/finance/`, `agent/bounty/` | Paper trading + bounty scaffolding; **$0 real career ROI** |

### Current career pipeline (as implemented)

```text
vacancy boards / TG channels
        ↓
   score vs resume.json
        ↓
   job_leads (SQLite)
        ↓
   /jobs list + /cover draft
        ↓
   [manual paste by user]
```

Missing by design for the new goal: **company discovery, people discovery, hidden hiring signals, personalized outreach CRM, approve-gated send, conversion tracking to money.**

### Evidence from last ~3 weeks of agent runs (server)

- Daily cycle runs; site healthy.
- Job leads mostly from Telegram; applications = 0.
- Bounty: 30 drafts rejected, 0 pending submits.
- Finance: paper only; A4 checkout sandbox ≠ live revenue.
- Resume sync: HH applicant API dead; digest-only for HH.

**Conclusion:** bottleneck is not code quality or React skill — it is **deal flow + positioning + outreach**.

---

## 2. Strengths (keep and leverage)

1. **Named enterprise proof** — X5 Tech, BI.ZONE, NLMK, Citilink (complex UI, RBAC, GraphQL, e-com migration).
2. **Product ownership cases** — sendonate (Mini App + cabinet + OBS), POTALONU seat-map (seats.io-like), PREEGLOS ticketing.
3. **Typed API / production craft** — Orval/OpenAPI, Keycloak, WebSocket, Vite migrations, Sentry, CI/CD.
4. **Self-hosted personal-stack** — rare signal: can ship full systems (site + agent + Telegram + memory + VPN). Use as *proof of autonomy*, not as primary product pitch until market-validated.
5. **Approve-gate pattern** — already proven for bounty; reuse for outreach.
6. **Cover/resume skills** — `agent/skills/cover-letter/`, `resume-copy/`, review personas.
7. **Multi-source vacancy adapters** — reusable as *signals* feeding company entities (not as the whole system).
8. **Telegram ops UX** — daily report + command pattern ready for company shortlist.

---

## 3. Weaknesses

| Weakness | Impact |
|----------|--------|
| Vacancy-only model | Misses hidden hiring / contract demand |
| No Company / Person / Outreach entities | Cannot run CRM or scoring |
| `/approve apply` never built | Pipeline stops at draft |
| Daily agent is bounty/income-first | Career work is not steered |
| Site = RU job-seeker + ASAP | Weak for intl CTO / client |
| 31 flat projects | Dilutes flagship signal |
| Title locked to “Senior Frontend” | Undersells product/ownership |
| English B1 on public resume | Hard filter for some intl roles |
| HH API closed; RPA deferred | No autopush resume/apply |
| No quantified outcomes | Harder Staff / $150k+ narrative |
| Finance/bounty noise | Competes for Cursor + attention |

---

## 4. Target positioning (decision)

### Primary profile (default)

**Senior Product Engineer (Frontend-leaning)**

Why this wins over alternatives:

| Option | Verdict |
|--------|---------|
| Senior Frontend Engineer | Too commodity; easy to price as mid-market |
| Full-stack Product Engineer | Strong secondary; use when Nest/Postgres/ownership is the sell |
| AI-augmented Product Engineer | Secondary for startups that already buy AI velocity; **do not** lead with “vibe coding” |
| Founding / early engineer | Targeted only for seed/Series A with CIS founders needing 0→1 |
| “Cursor expert” | Avoid as title — show as *delivery multiplier* in bullets |

**One-liner (working draft for EN):**

> Senior Product Engineer — I own complex React/TypeScript product surfaces end-to-end: typed API contracts, real-time UX, production delivery. I’ve shipped enterprise workflows at X5 / BI.ZONE / NLMK / Citilink and built multi-client products (Telegram Mini Apps, seat maps, streamer monetization) from idea to production.

**RU one-liner:**

> Senior Product Engineer (frontend-leaning) — сложные продуктовые интерфейсы на React/TypeScript: контракты API, real-time, production delivery. Enterprise (X5, BI.ZONE, НЛМК, Citilink) + собственные продукты (Mini Apps, схемы залов, monetization для стримеров).

### Secondary targeted versions (same master experience, different summary + highlights)

- **A** Senior Frontend / Product Engineer — enterprise hiring managers  
- **B** Full-stack Product Engineer — small teams needing ownership across FE+API  
- **C** AI-augmented Product Engineer — startups wanting velocity with Cursor/agents (evidence: personal-stack, delivery speed)  
- **D** Founding Engineer — early-stage, CIS-connected founders  

---

## 5. Target company profile

### Archetype (inspired by ANY.RUN, Rogii — expand beyond them)

**“International product company with CIS technical DNA”**

| Signal | Why it matters |
|--------|----------------|
| International legal entity (US, EU, UAE, etc.) | Payment path in USD/EUR |
| Founders / CTO / large eng share with RU/CIS background | Higher probability of hiring from Russia |
| Remote / distributed history | Fits RF resident |
| Active product + eng growth | Budget for seniors |
| Complex domain UI (security, industrial, SaaS ops, fintech, infra) | Match to your cases |
| Pays contractors or employs via intl entity | Path to ₽500k–1M |

### Seed examples (sources — not claims of open roles for you)

**ANY.RUN**

- Product: interactive malware sandbox ([any.run/about-us](https://any.run/about-us/)).
- LinkedIn company data: HQ Dubai; distributed workforce across many countries incl. Russia/Kazakhstan/Belarus (LinkedIn company page `any-run`).
- Public job posts (e.g. Embit) historically offered remote “country doesn’t matter” + Ulyanovsk office option — **TODO:** verify current openings before outreach.
- Fit reason: BI.ZONE GraphQL/SOC UI adjacency; product company; intl entity; CIS hiring culture signals.

**Rogii**

- Product: upstream oil & gas geosteering / Solo Cloud ([rogii.com](https://rogii.com/)).
- HQ Houston; multi-country presence; large software org cited in industry interviews ([Mexico Business News](https://mexicobusiness.news/oilandgas/news/digital-maturity-driving-og-efficiency-frontier)).
- Public roles often onsite-heavy (Built In) — **TODO:** validate which teams hire remote CIS contractors before scoring high.
- Fit reason: complex operational/domain UI (similar to NLMK production SPA pattern); product SaaS.

**Rule:** every company card must store `source_urls` and `evidence_*`. No invented CIS connections.

### Anti-targets (low priority)

- Pure body-shop outstaff without product ownership  
- Companies that only hire via RU payroll with no intl path (unless temporary bridge)  
- Mass HH spam mid-market “React developer” roles < market target  
- Crypto trading / bounty as career strategy (parked)

---

## 6. Company scoring model (explainable)

Score = weighted sum 0–100. Each factor stores **evidence strings**.

| Factor | Weight | Evidence examples |
|--------|--------|-------------------|
| CIS / RU connection | 20 | Founder birthplace/education; eng LinkedIn locations; RU language careers page; historical RU jobs |
| Hire-from-Russia probability | 15 | Past employees in RU; remote-from-anywhere posts; Embit/HH history |
| Remote / contract compatibility | 15 | Remote-first page; contractor language; multi-country eng |
| Technical fit | 15 | React/TS/Next in stack; domain UI complexity |
| Comp potential | 10 | Funding band if known; stage (Series B+ / profitable SaaS); US/EU rates |
| Company quality | 10 | Product traction, customers, funding, reputation |
| Hidden hiring probability | 10 | Recent eng hires without open FE role; “we're hiring” posts; team growth |
| Relevance to your cases | 5 | Security / industrial / e-com / Mini Apps / real-time |

**Shortlist rule:** score ≥ 70 **or** (CIS≥15 and tech fit≥10) with human review.

**Explain output example:**

> Score 78 — CIS founders + 4 eng with prior RU employers (LinkedIn public); remote-first careers page; React in stack from GH org; no open FE role but 3 eng hires in 90d (growth signal).

---

## 7. Discovery pipeline

```text
LEVEL 1 — Research automation
  seeds (manual + adapters)
      ↓
  company normalize (domain, LinkedIn, GH)
      ↓
  enrichment (stack, size, remote, CIS evidence)
      ↓
  score + explain
      ↓
  shortlist (status=candidate)

LEVEL 2 — Decision support
  research brief
  people candidates
  message angles

LEVEL 3 — Human approval
  /approve company <id>
  /approve contact <id>
  /approve outreach <id>

LEVEL 4 — Outreach (only after approve)
  send (manual or assisted)
  track replies / follow-ups
```

### Seed sources (priority, ToS-safe)

1. Official sites / careers pages  
2. GitHub orgs (stack, activity)  
3. Public LinkedIn company pages (manual or approved tools — **no aggressive scrape**)  
4. Wellfound / YC directory / Product Hunt  
5. Existing vacancy adapters → extract **employer** as company seed (HH/Habr/Hirify/HireHi/TG)  
6. Telegram hiring channels (company mentions)  
7. X/Twitter company accounts (light)  

**Reuse:** `job_hunt/scanner.py` employer fields become `Company` seeds, not the end state.

---

## 8. People discovery pipeline

```text
company (approved or high-score)
    ↓
roles: Founder, CTO, VP Eng, EM, Recruiter
    ↓
public profiles (LI / site / GH / TG)
    ↓
role relevance + contact channel
    ↓
research brief (no send)
    ↓
/approve contact + /approve outreach
```

**Brief must include:** who, role, background (sourced), company why, your relevance, concrete hook, message angle, channel (email/LI/TG), risk notes.

**Anti-spam:** ≤ N new outreaches/week (start: 5–10); personalized only; no blast.

---

## 9. Outreach pipeline

| Stage | Owner | System |
|-------|-------|--------|
| Draft message | Agent | templates + skills |
| Approve | You | Telegram |
| Send | You or assisted after approve | track in SQLite |
| Follow-up D+3 / D+7 | Agent reminder | Telegram |
| Reply → conversation | You | status update |
| Interview / contract | You | Opportunity status |

Channels: email (preferred for intl), LinkedIn InMail/connect (manual), Telegram (RU/CIS founders).

---

## 10. Resume strategy

### Master profile

- Single factual experience base (`resume-data.ts` / `resume.json`).
- Targeted **summaries + selected bullets + project highlights** per profile A–D.
- Remove/minimize: DOB on EN, Bitrix/jQuery laundry list, ASAP as default EN badge.

### Immediate content moves (P0)

1. Title → **Senior Product Engineer** (EN/RU) with Frontend-leaning subtitle.  
2. Add 1–2 **quantified or scoped** outcomes per flagship role (ask you for numbers if missing — never invent).  
3. Flagship projects only in primary PDF (6 max).  
4. Separate EN packaging for intl CTO (less ASAP, more ownership).  
5. HH digest blocks regenerated from master (manual paste still required).

### ATS vs founder PDF

- ATS: keywords React TypeScript Next.js GraphQL WebSocket OpenAPI Keycloak.  
- Founder: ownership narrative + personal-stack as autonomy proof (short).

### 10a. Why the current resume reads mid-level (diagnosis)

Feedback «мидловое» is mostly **packaging**, not lack of senior work. Concrete tells in current `resume.md` / `resume-data.ts`:

| Mid tell | Where | Fix (surgical) |
|----------|-------|----------------|
| Job title = «Frontend-разработчик» everywhere | All employers | → «Senior Product Engineer» / «Senior Frontend Engineer» with ownership language |
| Soft verbs | Citilink «Участвовал»; X5 «Делал задачу»; BI.ZONE «Развивал» | Strong verbs: Built / Shipped / Owned / Migrated — keep same facts |
| Outcomes = system description, not impact | All «Результат» | Prefer scope/ownership; add numbers **only** if you confirm |
| Skills laundry list | Bitrix, jQuery, WordPress beside FSD/MF | Core senior stack only; CMS/legacy → «Earlier» or omit on HH |
| Process prose | Long «Роль» paragraphs | 3–5 bullets/job; cut filler |
| DOB + ASAP + B1 | Header | Drop DOB on public; ASAP OK for HH; B1 keep honest |
| Education first impression | Non-CS college | Keep, but below experience; don’t lead with it on HH |
| Short POTALONU tenure on top | 09.2025–06.2026 | Frame as product ownership / contract delivery, not job-hop |

**Anti-slop rules for the next edit:**

1. One master RU text → site + HH + Habr + LI (EN separate, shorter).  
2. Change **titles, summary, verbs, skills trim, bullet shape** — do **not** regenerate whole career from scratch.  
3. Diff reviewable in git; you approve before platform paste.  
4. No invented % / users / $ without your OK.  
5. After merge: regenerate PDF + HH digest blocks from same source.

---

## 11. Website strategy

### Primary commercial story (pick for homepage)

**Hire + high-ticket contract** under one identity: Product Engineer who ships production systems — not “available ASAP React dev.”

### Concrete changes

1. Hero: one value sentence + scope; dual CTA — “Hiring managers: Resume/PDF” / “Founders & clients: Telegram”.  
2. Featured work: ≤6 flagships (X5, BI.ZONE, NLMK, Citilink, sendonate, seat-map).  
3. Archive Bitrix-era and SmartFish fragments behind “Earlier work”.  
4. Case study pages for 4–6 flagships (problem → decisions → outcome).  
5. Soften EN ASAP; keep RU urgency optional.  
6. Blog: don’t lead EN homepage with CEX trading; agent post only as “how I build systems”.  
7. Resolve GitHub username brand (`mpeshehonov` vs `mpeshekhonov`) — verify before linking prominently.

### Funnel metrics

- Profile views / PDF downloads  
- Telegram inbound quality  
- Outbound reply rate  
- Interviews / paid intros per month  

---

## 12. 30-day plan

**Goal:** positioning locked + CRM skeleton + first 30 scored companies + 10 approved outreaches.

| Week | Focus |
|------|--------|
| 1 | Freeze finance/bounty as primary; flip daily priorities to career; write positioning; resume summary v1 |
| 2 | Schema + SQLite entities; seed ANY.RUN, Rogii + 20 similar; score with evidence |
| 3 | Site homepage compress + CTAs; 6 flagship project taxonomy live |
| 4 | People briefs for top 10; outreach drafts; you approve/send ≥10 |

**Exit criteria:** ≥30 companies in DB with scores; ≥10 outreaches sent; ≥2 conversations started.

---

## 13. 90-day plan

**Goal:** steady pipeline toward ₽500k trajectory (mix of offers + contracts).

- 100+ companies researched; 40 shortlisted  
- 40+ outreaches; ≥15 replies; ≥5 interviews / paid discovery calls  
- 1–2 contract proposals OR late-stage employment process  
- Resume versions A/B live; EN case studies  
- Playwright HH/Habr/LI (user-approved ban risk) for volume on RU boards after master resume is live  
- Optional: product interviews only if employment pipeline stalls  

**Money path:** prioritize **contract retainers / employment offers in USD/EUR** over product speculation.

---

## 14. 180-day plan

**Goal:** ≥ ₽500k/mo stable (salary equiv. or contract mix).

- Either: intl remote offer ≥ target OR 1–2 clients covering target  
- Product lane: only if ≥3 paying customer interviews validated a problem (else kill)  
- System runs Level 1–3 weekly with minimal babysitting  

**12-month (₽1M):** raise rate/level (Staff-equivalent scope or parallel contracts); not “more React courses.”

---

## 15. Metrics / KPIs

| KPI | 30d | 90d | Notes |
|-----|-----|-----|-------|
| Companies scored | 30 | 100 | with evidence |
| Shortlist ≥70 | 10 | 40 | |
| Outreaches sent | 10 | 40 | approved only |
| Reply rate | ≥20% | ≥20% | |
| Conversations | 2 | 15 | |
| Interviews / paid calls | 1 | 5 | |
| Offers / signed contracts | 0–1 | 1–2 | |
| Pipeline $ (weighted) | — | ≥ ₽500k/mo potential | |
| Realized income | track | ≥ ₽500k/mo by M6 | |

**North star:** quality opportunities × conversion to money — not LOC or agent hours.

---

## 16. Technical implementation plan (after approval)

### Reuse, don’t rewrite

| Existing | New use |
|----------|---------|
| `state.py` SQLite + approve pattern | Company/Person/Opportunity/Outreach tables |
| `job_hunt/scanner.py` | Employer → Company seed |
| `matcher.py` idea | Company scoring weights |
| `drafter.py` + cover-letter skill | Outreach drafts |
| `resume_source.py` | Personalization context |
| Telegram bot | `/companies`, `/brief`, `/approve company|contact|outreach` |
| Daily report | Career section replaces finance-first |
| Site resume/projects | Positioning + flagship funnel |

### New modules (proposed)

```text
agent/career/
  companies.py      # CRUD + normalize
  discovery.py      # seeds + enrichment adapters
  scoring.py        # explainable score
  people.py         # decision makers
  briefs.py         # research briefs
  outreach.py       # drafts + status
  telegram_cmds.py  # or wire in bot.py
```

### Daily harness changes

1. Context pack: `career_backlog` + company shortlist (not bounty-first).  
2. Validator section: **Карьера** (or rename Финансы → optional weekly).  
3. `JOBHUNT_ENABLED` on; finance paper weekly; bounty idle-only.  
4. Cap Cursor: career tasks before bounty hunt.

### Explicit non-goals (now)

- Mass LinkedIn scrape  
- Autonomous message send without approve  
- Crypto trading / bounty as career KPI  
- Full rewrite of orchestrator  
- Fake HH API revival  

### Constraints locked (2026-07-20, user)

1. **Title:** Senior Product Engineer (Frontend-leaning) — approved.  
2. **Comp target:** **$3–4k USD/month** is a strong near-term win; maximize upward.  
3. **Payment rails OK:** самозанятый РФ · ТК РФ (официальное трудоустройство) · **USDT**.  
4. **Playwright HH/Habr/LI RPA:** **approved** (user accepts ban risk; Sofi-class approach).  
5. **Priority next 6 months:** **find a job ASAP** (employment or contract); earnings > purity of lane mix.  
6. **Resume policy:** surgical upgrade of one master profile for site + HH + Habr + LinkedIn — **no full AI rewrite** (slop risk). See §10a.

### Still TODO (facts only)

1. Current open roles at ANY.RUN / Rogii / similar before outreach.  
2. Quantified metrics you can defensibly claim (users, latency, team size, GMV) — ask before inventing.  
3. English for live interviews vs public B1 line (keep honest; optional soften on HH).  

---

## Architecture change (summary diagram)

```text
BEFORE:  vacancy → match → cover → (manual)

AFTER:   company discovery → score → people → brief
              ↓
         open roles + hidden demand
              ↓
         personalized outreach (approve)
              ↓
         conversation → interview/contract
              ↓
         money (KPI)
```

Vacancy scan remains a **feed into Company**, not the product.
