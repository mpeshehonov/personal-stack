---
name: resume-copy
description: Rewrite resume and portfolio bullets for ATS and human readers. Use when editing resume-data.ts, resume.md, project case studies, or CV bullets.
---

# Resume copy

## Goal

Bullets pass ATS keyword filters and read clearly to a tech lead in 6 seconds. No fluff, no AI tells.

## Bullet formula

**Verb + what + tech/context + result** (15–25 words, 1–2 lines)

Example:
- Bad: `Участвовал в разработке модуля согласования закупок`
- Good: `Собрал UI модуля НКЗ 3.0: RBAC, статусы, Orval по OpenAPI, Vite code splitting на длинных сценариях`

## Verbs (past tense for past roles)

Built, Shipped, Migrated, Optimized, Implemented, Integrated, Refactored, Designed, Architected, Reduced, Automated.

Avoid: «Спроектировал и реализовал» in every bullet, «Responsible for», «Worked on», «Participated in».

## ATS rules

1. Mirror job keywords naturally (React, TypeScript, REST API, GitLab CI, npm, Jest) — not keyword stuffing.
2. List both `React` and framework names where relevant; include `JavaScript` and `TypeScript`.
3. Name concrete tools in bullets, not only in skills section.
4. Quantify when defensible: bundle size, tables rows, teams, modules, deploy time. No invented percentages (e.g. 15% conversion) without source.
5. Plain language — no paths (`/embed/...`), no internal codenames unless public product name.
6. No long dashes (—) and no curly quotes in RU copy; use hyphen or comma.

## Project / experience block structure (site)

Match `ProjectCard` layout:

| Field | Purpose |
|-------|---------|
| tagline | One line value prop |
| problem | Context for HR |
| contribution | What you did (role) |
| outcomes | 2–3 result bullets with impact |
| stack | Tags, max 8 on card |

## RU and EN sync

Update together:
- `site/lib/resume-data.ts` — live /resume
- `site/content/resume/resume.md` + `en/resume.md` — PDF source
- `site/content/projects/index.json` — case cards
- `site/lib/skills.ts` — skill groups

Regenerate PDF: copy md to `~/personal/cv/`, `make resume-main`, copy to `site/public/`.

## Source of truth for projects

`~/personal/cv/projects.md` — all projects must appear on `/projects`, ranked best → weakest; games and pet projects last.

**Public site:** sensitive or NDA work uses generic titles only (e.g. `marketplace-nda`). Do not publish client names, domains, or product themes (escort/adult, etc.). Private ids like `auraescort` map to `marketplace-nda` on the site — one card, no duplicate.

## Experience vs projects (timeline policy)

- **`/resume` experience:** last **5 employers only**, with dates (POTALONU → X5 → BI.ZONE → NLMK → Citilink).
- **Everything else** (Citilink, In2View, Bitrix shops, side gigs, parallel work): **projects only**, no dates on project cards.
- **About block:** point to `/projects` vaguely («другие задачи и кейсы»); no company names or stack lists for that section.
- **Skills:** keep ATS keywords (1C-Bitrix, etc.) even when role is in projects, not experience.
- On **PDF / HH**: user may use a fuller timeline offline; site is intentionally shorter.

## Red flags (cut or rewrite)

- Stack dumps without action
- Repeated opener every bullet
- «Единый интерфейс» without saying for whom
- Fake metrics from old CV templates
- Vague words: значительно, много, successfully, proven track record, team player

## 15-second sell checklist

Full lesson: `agent/memory/lessons/resume_sells_in_15_seconds.md` (@money_career).

Quick: market title (+ aliases) → **goal line** (что ищу) → about who/can/seek/unique → company scale one-liner → 1-line achievement bullets → skills at bottom. No DOB. Recruiter first scans titles, dates, location — then stack.

## Multi-vacancy soft targeting (RF market)

When optimizing for several JDs at once (Bitrix + React + e-commerce + fullstack):

| JD theme | Mirror honestly in summary, skills, 1–2 bullets |
|----------|--------------------------------------------------|
| 1C-Bitrix / web on Bitrix | `1C-Bitrix`, компоненты/шаблоны, PHP, jQuery, SCSS, Webpack, MySQL, интернет-магазин; roles Maximaster + Energosoft |
| React / JS frontend | `React`, `TypeScript`, `JavaScript`, `HTML5`, `CSS3`, REST API, Git, code review |
| E-commerce | Citilink, Bitrix shops, marketplace-nda, каталог/корзина/фильтры, опт/розница |
| Python + React | `Python (Django REST)` only where true (sendonate); `SQL`, PostgreSQL, REST |
| Enterprise / gov-style | X5, NLMK, BI.ZONE; Scrum, GitLab CI, Keycloak, RBAC |

**Do not claim:** Vue, Bitrix24 modules, Bitrix certificates, 3+ years Python, RabbitMQ, Elasticsearch unless verified.

**RU ATS:** verbatim strings from JD (`1C-Bitrix`, `REST API`, `Git`, `интернет-магазин`) in summary + skills + experience. HR scans summary in 6s; tech lead reads outcomes.

**Strong bullet test:** Can you defend it in an interview? Does it name tool + action + who benefited?
