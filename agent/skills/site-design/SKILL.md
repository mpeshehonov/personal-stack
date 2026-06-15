---
name: site-design
description: Design system for mpeshekhonov.ru — Tailwind tokens, motion, layout. Use for any site/ UI change in site/.
---

# Site Design System

Load before editing `site/`. Goal: **consistent, calm portfolio** — not feature spam.

## Principles

1. **Reuse before invent** — `card`, `btn-primary`, `section-label`, `FadeIn`, existing components.
2. **One idea per section** — no duplicate CTAs (e.g. don't add a second PDF banner if resume header already has actions).
3. **Motion with purpose** — `FadeIn` for section entrance only; respect `prefers-reduced-motion`.
4. **Hierarchy** — eyebrow (`section-label`) → title (`section-title`) → body (`text-ink-muted`).
5. **Print-aware** — resume uses `resume-print` + `print:hidden` on nav actions.

## Tokens (globals.css + tailwind)

| Class | Use |
|-------|-----|
| `card` | Content blocks, subtle shadow |
| `btn-primary` / `btn-secondary` | Main / secondary actions |
| `section-label` | Eyebrow, mono, accent |
| `section-title` | H2 page sections |
| `text-ink` / `text-ink-muted` / `text-ink-faint` | Text hierarchy |
| `accent` / `accent-soft` | Links, tags, gradients |
| `prose-blog` | Blog article body only |

## Hero pattern

```tsx
<div className="card relative overflow-hidden border-0 bg-gradient-to-br from-surface via-surface to-accent-soft p-8 sm:p-10">
  <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-accent/10 blur-3xl" aria-hidden />
  ...
</div>
```

## Anti-patterns (do NOT)

- Extra gradient banners duplicating existing header actions
- Raw hex colors — use Tailwind tokens
- `animate-bounce`, heavy parallax, carousel without request
- New npm UI libs without approval
- Breaking i18n — always `dict` + `localizedPath(locale, ...)`
- English hardcoded strings on RU pages

## Blog

- Use `BlogPostHeader` for post pages
- Article width `max-w-3xl`, `prose-blog` for markdown
- Back link in `<nav>` with clear spacing from `<time>`

## Checklist before commit

- [ ] RU + EN routes work
- [ ] Mobile layout (flex-wrap, gap)
- [ ] No duplicate CTAs on same page
- [ ] `npm run build` in `site/` passes
