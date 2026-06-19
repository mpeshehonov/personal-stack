---
name: cover-letter
description: Write job application cover letters for RF IT market (HH, Habr, email apply). Human tone, vacancy-specific hooks, no AI slop. Use when drafting отклик, сопроводительное письмо, cover letter, or preparing email apply via job hunt.
---

# Cover letter (сопроводительное)

## Goal

A recruiter reads 50+ откликов. Yours should prove **fit in 15 seconds**: one relevant hook, one proof, one clear ask. Not a second resume, not ChatGPT tone.

## When to use

- Vacancy asks for email apply (`hr@…`, `jobs@…`, direct recruiter mail)
- HH/Habr отклик with optional cover letter field
- `/approve apply <id>` flow in job hunt (draft before send)
- User pastes vacancy text and asks for сопровод

## Inputs (read before writing)

1. Full vacancy text (title, company, requirements, nice-to-have, format)
2. `site/content/resume/resume.json` — summary + skills for keyword mirror
3. `site/lib/resume-data.ts` — pick **one** experience block + **one** project that match this JD (do not dump all employers)
4. Contact email from vacancy; if missing, ask user
5. Apply channel: email / HH form / Telegram — affects length and sign-off

**Hard rules:** only facts from resume and projects. No invented employers, years, or tools. No Vue, Bitrix24, 3+ years Python unless in resume.

## Structure (RU email apply, 120–180 words)

```
Тема: Frontend-разработчик — [Имя] / [ключевое из JD, 3–5 слов]

Здравствуйте!

[1 предложение: роль + почему эта компания/продукт — конкретно из текста вакансии, не «интересная компания»]

[2–3 предложения: один релевантный кейс — компания или продукт, стек из JD, результат без выдуманных цифр]

[1 предложение: формат — удалённо, Сочи, готов к выходу ASAP если уместно]

Резюме и кейсы: https://mpeshekhonov.ru/ru/resume
Telegram: @makusimu_san

С уважением,
Максим Пешехонов
+7 950 919-67-86
```

**Subject line:** `[Senior Frontend / React] — Максим Пешехонов` or mirror their title wording. No emoji, no ALL CAPS.

## Structure (HH / Habr short field, ≤500 chars)

- Line 1: grade + stack match (`Senior Frontend, React/TS/Next.js, 7+ лет`)
- Line 2: one proof bullet from best matching role
- Line 3: ссылка на сайт + ASAP / remote

## Tone (RF IT, 2026)

| Do | Don't |
|----|-------|
| Короткие предложения, 12–20 слов | «Добрый день! Меня заинтересовала ваша вакансия…» |
| Конкретный продукт/задача из JD | «Я командный игрок с горящими глазами» |
| «Делал X на React/TS для Y» | «Обладаю обширным опытом в…» |
| «Готов обсудить» / «Могу соз созвон» | «Буду рад стать частью вашей динамичной команды» |
| «Удалённо, Сочи» если релевантно | Повтор всего резюме |
| Один стек-мост: Orval, Keycloak, e-commerce | Список из 15 технологий |

## Anti-slop checklist (must pass before output)

- [ ] No opening «Меня заинтересовала ваша вакансия» / «I am writing to express»
- [ ] No «уникальная возможность», «динамичная команда», «профессиональный рост»
- [ ] No em dash spam (—); max 1 in whole letter
- [ ] No bullet list longer than 3 items in email body
- [ ] At least one phrase **verbatim or paraphrased from JD** (their stack, domain, product)
- [ ] At least one **named proof** (X5 / Citilink / sendonate / BI.ZONE — pick one relevant)
- [ ] Word count 120–180 (email) or ≤500 chars (HH field)
- [ ] Sign-off matches channel (email: full contacts; HH: link only)

## Vacancy-type hooks (pick one)

| JD focus | Lead with |
|----------|-----------|
| React / Next e-commerce | Citilink migration, PREEGLOS checkout, URL/SEO filters |
| Enterprise / RBAC | X5 НКЗ Keycloak + Orval + long forms |
| Product / startup | sendonate 3 clients, WebSocket, CI/CD monorepo |
| Bitrix / CMS | projects section + Symfony/PHP background (not in experience dates) |
| Python + React | POTALONU Django REST integration, frontend-first framing |
| SOC / data-heavy UI | BI.ZONE Threat Intelligence, GraphQL, virtualization |

## Output format

Deliver to user/Telegram:

```markdown
## Draft — [Company] / [Title]

**To:** hr@example.com  
**Subject:** …

[letter body]

---
**Match notes:** (internal, optional) which resume block used, JD keywords hit
**Attachments:** resume PDF RU / EN — confirm before send
```

## Send gate (job hunt integration)

- Draft only — user sends manually (no agent SMTP)
- `/cover <id>` in Telegram generates draft; stored in `job_applications`
- Never send from agent without explicit user action outside bot

## Self-check with resume-copy

Same honesty rules as `agent/skills/resume-copy/SKILL.md`: no fake metrics, no keyword stuffing, RU plain language.

## Examples

Good vs bad letters and HH snippets: [examples.md](examples.md)
