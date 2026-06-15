# Site Improvement Backlog — Target 8/10

**Vision:** не визитка, а **portfolio + proof of work** — HR видит impact, стек и кейсы за 30 секунд.

## Done
- [x] Replace placeholder experience with real CV data
- [x] Add Open Graph meta tags for resume sharing
- [x] Improve mobile layout on /resume

## Milestone A1 — Structure (priority)

- [x] **SB-01** Homepage sections: Hero → Selected Work → Experience preview → Skills → CTA contact
- [x] **SB-02** `/projects` page — 3–5 case studies (X5, NLMK, Telegram Mini Apps, etc.) from resume data
- [x] **SB-03** `content/projects/*.json` single source for case cards
- [x] **SB-04** `/blog` route — MDX or contentlayer, list + post template
- [x] **SB-05** First blog post skeleton: «Self-hosted agent stack» (affiliate-ready)

## Milestone A2 — Visual polish

- [x] **SB-06** Typography scale + section spacing system (consistent 8/10 rhythm)
- [x] **SB-07** Subtle scroll animations (framer-motion, respect reduced-motion)
- [ ] **SB-08** Dark/light theme toggle
- [ ] **SB-09** Custom OG image per page (or dynamic `/api/og`)
- [x] **SB-10** Footer: availability badge («open to offers» / «busy»)

## Milestone A3 — Conversion

- [x] **SB-11** Prominent Telegram + email CTA on every page
- [x] **SB-12** `/resume` — downloadable PDF CTA above fold, print stylesheet
- [ ] **SB-13** Privacy-friendly visit counter (no Google Analytics)
- [x] **SB-14** JSON-LD Person schema for SEO

## Rules for agent

1. Max **2 site items per week** in daily cycle (quality > quantity)
2. Every case study needs: problem → role → stack → outcome (metric if possible)
3. Deploy via normal git flow; verify https://mpeshekhonov.ru after deploy
