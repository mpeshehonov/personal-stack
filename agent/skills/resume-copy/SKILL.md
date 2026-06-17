---
name: resume-copy
description: Rewrite resume and portfolio bullets to be clear, credible, and human. Use when editing resume-data.ts, resume.md, project case studies, or CV bullets.
---

# Resume copy

## Rules

1. **Plain language** — no paths (`/embed/...`), no internal codenames unless the product name is public (sendonate, PREEGLOS).
2. **One idea per bullet** — outcome or responsibility, not a stack dump.
3. **Credible scale** — avoid "hundreds of roles", "thousands of rows" unless you can defend the number. Prefer "different roles", "large datasets", "long approval flows".
4. **Strong verbs, varied openers** — не повторять «Спроектировал и реализовал» / «Designed and built» в каждом пункте.
5. **Metrics only when real** — no invented percentages (e.g. 15% conversion) without a source.
6. **RU and EN in sync** — update `site/lib/resume-data.ts`, `site/content/resume/resume.md`, `site/content/resume/en/resume.md`, and matching `site/content/projects/*.json` titles/outcomes.

## Bullet template

`[What you built]` + `[how / with what, briefly]` + `[result for user or team]`

Example:
- Bad: `embed-виджет /embed/[hallId], события и бронирования`
- Good: `Виджет выбора мест для сайтов партнёров — события и бронирования`

## Files to touch together

- `site/lib/resume-data.ts` — live /resume page
- `site/content/resume/resume.md` + `en/resume.md` — PDF source (sync via `scripts/sync-resume.sh` from ~/personal/cv when needed)
- `site/content/projects/index.json` — case cards on homepage
