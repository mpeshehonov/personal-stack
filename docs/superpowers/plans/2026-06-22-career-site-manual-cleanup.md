# Career Site Manual Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove daily-agent homepage additions, add phone visibility, block autonomous site edits, and store fresh project facts for future career copy.

**Architecture:** Keep homepage composition in `site/app/[locale]/page.tsx` focused on existing career sections. Put phone contact into `SocialLinks` so it appears wherever the shared contact component is used. Daily-agent behavior is controlled by prompt/memory files, not runtime code.

**Tech Stack:** Next.js App Router, TypeScript, JSON dictionaries, Markdown memory/docs, git deploy flow.

---

## File Structure

- Modify `site/app/[locale]/page.tsx`: remove `BlogPreview`, `ProductTeaser`, and `getLatestBlogPosts` usage from homepage.
- Delete `site/components/BlogPreview.tsx`: no longer used after homepage removal.
- Delete `site/components/ProductTeaser.tsx`: no longer used after homepage removal.
- Modify `site/components/SocialLinks.tsx`: add phone link with `tel:+79509196786`.
- Modify `site/content/i18n/ru.json` and `site/content/i18n/en.json`: remove homepage-only product/blog preview labels if no longer referenced.
- Modify `agent/tasks/daily_prompt.md`: remove autonomous site-improvement lane; keep health/redeploy only.
- Modify `agent/memory/INDEX.md`: replace "Max 1-2 site improvements per day" with manual-only site rule.
- Create `agent/memory/career-copy-notes.md`: store recent project facts for later resume/projects/blog/cover-letter work.

---

### Task 1: Remove Homepage Product And Blog Blocks

**Files:**
- Modify: `site/app/[locale]/page.tsx`
- Delete: `site/components/BlogPreview.tsx`
- Delete: `site/components/ProductTeaser.tsx`

- [ ] **Step 1: Update homepage imports and data**

Remove these imports:

```ts
import { BlogPreview } from "@/components/BlogPreview";
import { ProductTeaser } from "@/components/ProductTeaser";
import { getLatestBlogPosts } from "@/lib/blog";
```

Remove this local variable:

```ts
const latestPosts = getLatestBlogPosts(2);
```

- [ ] **Step 2: Update homepage JSX**

Remove these two lines from the returned fragment:

```tsx
<BlogPreview locale={locale} dict={dict} posts={latestPosts} />
<ProductTeaser locale={locale} dict={dict} />
```

The homepage order must become:

```tsx
<Hero locale={locale} dict={dict} resume={resume} />
<SelectedWork locale={locale} dict={dict} projects={featuredProjects} />
<ExperiencePreview locale={locale} dict={dict} experiences={previewExperiences} />
<FadeIn className="section">
  <p className="section-label">{dict.sections.skills}</p>
  <h2 className="section-title mb-3">{dict.sections.skills}</h2>
  <p className="mb-8 max-w-2xl text-ink-muted">{dict.sections.skillsDesc}</p>
  <SkillGrid groups={getSkillGroups(locale)} />
</FadeIn>
```

- [ ] **Step 3: Delete unused components**

Delete:

```text
site/components/BlogPreview.tsx
site/components/ProductTeaser.tsx
```

- [ ] **Step 4: Verify no imports remain**

Run:

```bash
rg "BlogPreview|ProductTeaser|getLatestBlogPosts" site
```

Expected: no matches except none. If `getLatestBlogPosts` is still used elsewhere, keep `site/lib/blog.ts` unchanged.

---

### Task 2: Add Phone Link To Shared Social Links

**Files:**
- Modify: `site/components/SocialLinks.tsx`

- [ ] **Step 1: Add phone link to socials**

Change the `socials` array to include phone after Telegram:

```ts
const phoneLabel = locale === "en" ? "+7 950 919-67-86" : "+7 950 919-67-86";

const socials = [
  { href: resume.links.website, label: siteLabel, icon: "WWW", external: true },
  { href: resume.links.telegram, label: "Telegram", icon: "TG", external: true },
  { href: "tel:+79509196786", label: phoneLabel, icon: "TEL", external: false },
  { href: resume.links.linkedin, label: "LinkedIn", icon: "in", external: true },
  { href: resume.links.github, label: "GitHub", icon: "GH", external: true },
];
```

- [ ] **Step 2: Preserve `target` only for external links**

Update the map destructuring and anchor props:

```tsx
{socials.map(({ href, label, icon, external }) => (
  <a
    key={href}
    href={href}
    target={external ? "_blank" : undefined}
    rel={external ? "noopener noreferrer" : undefined}
    className="group flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-ink-muted backdrop-blur-sm transition-all hover:border-accent/30 hover:bg-accent/5 hover:text-accent"
  >
    <span className="font-mono text-xs font-bold text-accent/80 group-hover:text-accent">
      {icon}
    </span>
    {label}
  </a>
))}
```

- [ ] **Step 3: Verify phone link**

Run:

```bash
rg "tel:\\+79509196786|\\+7 950 919-67-86" site/components/SocialLinks.tsx
```

Expected: both phone href and display label are present.

---

### Task 3: Clean Homepage-Only Dictionary Keys

**Files:**
- Modify: `site/content/i18n/ru.json`
- Modify: `site/content/i18n/en.json`

- [ ] **Step 1: Remove unused RU keys**

Remove these keys from `sections`:

```json
"latestBlog": "Из блога",
"latestBlogDesc": "Заметки про инфраструктуру, agent stack и автономные finance lanes.",
"allPosts": "Все посты",
"productTeaser": "Продукт",
"productTitle": "Personal Stack Agent Starter",
"productTeaserDesc": "Self-hosted harness для AI-агентов: orchestrator, Telegram-бот, finance scan и deploy pipeline — без SaaS lock-in. Скоро на Gumroad.",
"productTeaserCta": "Подробнее в блоге",
"productTeaserEarlyAccess": "Ранний доступ"
```

- [ ] **Step 2: Remove unused EN keys**

Remove these keys from `sections`:

```json
"latestBlog": "From the blog",
"latestBlogDesc": "Notes on infrastructure, agent stack, and autonomous finance lanes.",
"allPosts": "All posts",
"productTeaser": "Product",
"productTitle": "Personal Stack Agent Starter",
"productTeaserDesc": "Self-hosted AI agent harness: orchestrator, Telegram bot, finance scan, and deploy pipeline — no SaaS lock-in. Coming to Gumroad.",
"productTeaserCta": "Read on the blog",
"productTeaserEarlyAccess": "Early access"
```

- [ ] **Step 3: Validate JSON**

Run:

```bash
python3 -m json.tool site/content/i18n/ru.json >/dev/null
python3 -m json.tool site/content/i18n/en.json >/dev/null
```

Expected: both commands exit with code 0.

---

### Task 4: Disable Autonomous Site Improvements In Daily Agent

**Files:**
- Modify: `agent/tasks/daily_prompt.md`
- Modify: `agent/memory/INDEX.md`

- [ ] **Step 1: Update `daily_prompt.md` planning limits**

Replace:

```markdown
Максимум **1 пункт site_backlog + 1 пункт income_backlog** за цикл. Bounty hunt — только orchestrator.
```

with:

```markdown
Сайт не улучшать автономно: только health/redeploy, если прод лежит. Любые copy/design/feature изменения сайта — только вручную с пользователем. Максимум **1 пункт income_backlog** за цикл. Bounty hunt — только orchestrator.
```

- [ ] **Step 2: Update `daily_prompt.md` priority list**

Replace priorities 2-7 with:

```markdown
2. **Income** — ≤1 пункт из `agent/tasks/income_backlog.md` (skill: income-harness)
3. **Job hunt** — не дублировать scanner; только backlog если включено
4. **Bounty** — краткий итог в логе; hunt не запускать
5. **Finance** — JSON proposals для risk engine (English JSON)
6. **Memory** — уроки в `agent/memory/lessons/` при повторяющихся сбоях
```

- [ ] **Step 3: Update checkpoints**

Replace:

```markdown
- [ ] ≤1 site + ≤1 income change
```

with:

```markdown
- [ ] Сайт не менялся автономно, кроме emergency health/redeploy
- [ ] ≤1 income change
```

- [ ] **Step 4: Update `agent/memory/INDEX.md` rules**

Replace:

```markdown
3. Max 1-2 site improvements per day
```

with:

```markdown
3. Сайт не улучшать автономно: copy/design/feature изменения только вручную с пользователем; daily может делать только health/redeploy если сайт лежит
```

- [ ] **Step 5: Verify no autonomous site backlog instruction remains**

Run:

```bash
rg "site_backlog|Max 1-2 site|≤1 site|Site.*≤" agent/tasks/daily_prompt.md agent/memory/INDEX.md
```

Expected: no matches.

---

### Task 5: Store Career Copy Notes

**Files:**
- Create: `agent/memory/career-copy-notes.md`

- [ ] **Step 1: Create memory note**

Create the file with this content:

```markdown
# Career Copy Notes

Use these facts later for project pages, cover letters, resume bullets, and frontend/fullstack blog topics. Do not publish them directly without rewriting and checking facts with the user.

## Recent project facts

- `akvaprom.kg`: built an online store for aquaculture/fish-farm products. Recent proof points: bonus system, promo codes, and SEO result where the site reached the first page of Yandex.
- `sendonate.com`: shipped many streamer-cabinet updates, donation widget designs, and broader streamer functionality around donations, alerts, and cabinet workflows.
- `potalonu.com`: built a custom seats.io-like service for events: create venue halls, embed a seat selection widget into event sites, and support seat selection/purchase flows.

## Future content angles

- Case study: "How I built a seats.io-like hall editor and embeddable seat picker for events."
- Case study: "E-commerce on Next.js with bonuses, promo codes, and SEO growth for akvaprom.kg."
- Case study: "Streamer monetization UI: donation widgets, OBS overlay, Telegram Mini App, and cabinet workflows."
```

- [ ] **Step 2: Verify memory note exists**

Run:

```bash
test -f agent/memory/career-copy-notes.md && rg "akvaprom|sendonate|potalonu" agent/memory/career-copy-notes.md
```

Expected: all three names are found.

---

### Task 6: Validate, Commit, Deploy

**Files:**
- Validate all files from Tasks 1-5.

- [ ] **Step 1: Run lints/build**

Run:

```bash
cd site && npm run build
```

Expected: build exits with code 0.

- [ ] **Step 2: Check IDE lints**

Use `ReadLints` for:

```text
site/app/[locale]/page.tsx
site/components/SocialLinks.tsx
```

Expected: no new errors.

- [ ] **Step 3: Commit implementation**

Run:

```bash
git add site/app/[locale]/page.tsx site/components/SocialLinks.tsx site/content/i18n/ru.json site/content/i18n/en.json agent/tasks/daily_prompt.md agent/memory/INDEX.md agent/memory/career-copy-notes.md
git add -u site/components/BlogPreview.tsx site/components/ProductTeaser.tsx
git commit -m "fix(site): remove daily homepage additions and add phone contact"
```

- [ ] **Step 4: Deploy**

Run:

```bash
./scripts/deploy-local.sh
```

Expected:

- push succeeds
- remote deploy succeeds
- site health check passes

- [ ] **Step 5: Post-deploy smoke check**

Run:

```bash
curl -fsSL https://mpeshekhonov.ru/ru | rg "Personal Stack Agent Starter|Из блога|\\+7 950 919-67-86"
```

Expected:

- `+7 950 919-67-86` is present
- `Personal Stack Agent Starter` is absent
- `Из блога` is absent

If the `rg` command exits non-zero because only absent strings are checked, run separate checks:

```bash
curl -fsSL https://mpeshekhonov.ru/ru | rg "\\+7 950 919-67-86"
! curl -fsSL https://mpeshekhonov.ru/ru | rg "Personal Stack Agent Starter|Из блога"
```

---

## Self-Review

- Spec coverage: homepage cleanup in Task 1, phone in Task 2, dictionary cleanup in Task 3, daily-agent guard in Task 4, memory facts in Task 5, validation/deploy in Task 6.
- Placeholder scan: no TBD/TODO placeholders.
- Scope check: large career system, blog rewrite, HH/LinkedIn/Habr automation, and resume rewrite are intentionally out of scope.
