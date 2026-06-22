# Career site manual cleanup design

Date: 2026-06-22

## Goal

Remove unexpected daily-agent additions from the career site and make future site improvements manual-only. The site should stay focused on selling Maksim as a Senior Frontend / Fullstack engineer, not on internal products, finance experiments, or agent infrastructure.

## Current Context

`origin/main` added two homepage sections from the daily agent:

- `ProductTeaser` with "Personal Stack Agent Starter"
- `BlogPreview` with recent blog posts

The blog currently contains agent/finance-heavy posts that are not strong proof for frontend/fullstack hiring. Daily instructions also still allow regular site improvements, which can create unexpected changes.

## Recommended Approach

Do a small cleanup now and defer the larger career-system redesign.

This means:

- remove product and blog preview sections from the homepage
- add phone number visibility to the site
- prevent daily agent from changing the site without explicit manual work
- store recent project facts for later rewrite of projects, cover letters, and blog
- leave the blog route available, but do not feature it on the homepage until it has hiring-focused posts

## Homepage Design

Keep the homepage structure simple:

1. Hero
2. Selected Work
3. Experience Preview
4. Skills
5. Projects CTA

Remove from homepage:

- `ProductTeaser`
- `BlogPreview`
- related dictionary labels used only by those homepage blocks if no other route needs them

Do not delete blog pages or product memory yet. The cleanup is about public presentation, not data loss.

## Contact Design

Add phone number `+79509196786` to the site alongside existing Telegram, email, GitHub, LinkedIn links.

Preferred placement:

- `SocialLinks` or shared contact component, so the number appears consistently where contact links are shown
- keep the phone as `tel:+79509196786`
- display format can stay `+7 950 919-67-86` for readability

Do not remove existing Telegram or email.

## Blog Design

Short term:

- remove blog preview from homepage
- keep `/blog` route available
- keep existing posts unless they actively harm the site

Future blog direction:

- frontend/fullstack case studies
- practical engineering posts tied to projects
- posts that prove React, Next.js, TypeScript, integrations, performance, product delivery

Avoid homepage promotion until there are 2-3 strong hiring-focused posts.

## Daily Agent Design

Daily agent should not make site improvements by default.

Change daily planning rules so:

- health checks can still detect if the site is down
- deploy/recovery can still happen if the site is broken
- planned feature/copy/design changes to the site are excluded from daily autonomous work
- site improvements happen only through manual sessions with explicit user approval

This should be expressed in `agent/tasks/daily_prompt.md` and the memory index rule section.

## Memory Design

Record these facts for future career copy:

- `akvaprom.kg`: online store with bonus system and promo codes; reached first page in Yandex
- `sendonate.com`: many streamer cabinet updates, donation widget designs, broader streamer functionality
- `potalonu.com`: custom seats.io-like service for creating event halls and embedding seat selection/purchase widget into event sites

Store this in a small memory note, not as public site copy yet. The future rewrite can turn these into stronger project bullets, cover-letter hooks, and blog topics.

## Data Flow

Manual workflow after implementation:

1. User gives site/career direction.
2. Agent updates source files.
3. Site and PDFs are regenerated when resume data changes.
4. Changes are committed and deployed.
5. Daily agent only monitors health and income/job-hunt lanes, not site copy/features.

## Error Handling

- If removing homepage sections leaves unused imports, fix TypeScript/build errors.
- If dictionary keys become unused but harmless, prefer leaving them until a focused cleanup unless lints fail.
- If daily agent still changes site after rules update, add a stricter validator or explicit deny-list in a later task.

## Validation

Run:

- site build or typecheck
- lint diagnostics for edited files
- verify homepage no longer renders product/blog blocks
- verify phone link is visible and uses `tel:+79509196786`
- verify daily prompt no longer assigns site backlog work

## Out Of Scope

- full master resume / career system
- HH, LinkedIn, Habr browser automation
- full blog rewrite
- new visual design
- deleting blog route or all blog content

## Open Decisions

None for this cleanup. The larger career system needs a separate design.
