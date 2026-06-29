# Job automation without API (research, 2026-06)

> User note: HH applicant API closed 2025-12-15. Commercial tools (Sofi, JobTurbo, etc.) use **browser RPA**, not API.  
> **Decision deferred** — revisit when user returns.

## TL;DR

| Подход | HH отклики | HH резюме | Habr | LinkedIn | Риск |
|--------|------------|-----------|------|----------|------|
| **Playwright + storageState** | ✅ рабочий стандарт | ✅ | ✅ cookie | ⚠️ fragile | бан аккаунта |
| **CDP к реальному браузеру** (Яндекс/Chrome) | ✅ лучший anti-detect | ✅ | ✅ | ⚠️ | ниже detect |
| **Desktop app у пользователя** (как Sofi) | ✅ | ✅ | — | — | сессия на ПК юзера |
| **Официальный @hh_rabota_bot** | ❌ | поднять резюме | — | — | низкий |
| **Digest / ручное** | copy-paste | copy-paste | — | PDF | нулевой |

---

## Sofi Assistant — как реально работает после 15.12.2025

- Сайт: [sofi-assistant.com](https://sofi-assistant.com/landing/)
- На лендинге ещё пишут «официальный API» — **устаревший маркетинг**.
- В [Telegram «Софи и партнеры»](https://t.me/s/sofiandpartners): после закрытия API выпустили **desktop-приложение Win/Mac/Linux**, которое **полностью имитирует действия пользователя** в браузере (листает вакансии, жмёт отклик).
- Лимит ~20 откликов/день «умным» распределением; LLM для сопроводительных.
- Habr от founders: [как строили Софи](https://habr.com/ru/articles/953192/), [команда джунов](https://habr.com/ru/articles/948698/).

**Вывод для нашего стека:** не API-клиент, а **RPA на машине пользователя или RU VPS с резидентским IP + persistent browser profile**.

---

## Как делают все «выжившие» сервисы (2026)

Источники: [Habr 981764](https://habr.com/ru/articles/981764/), [JobTurbo 2026](https://jobturbo.ru/blog/avtootklik-na-hh-ru-2026), [Habr 983318 RPA](https://habr.com/ru/articles/983318/), [vc.ru AI beta](https://vc.ru/hr/2769138-avtomatizatsiya-otklikov-na-hh-ru-s-pomoshchyu-ai).

### Технический pipeline

```text
vacancy list (browser DOM / our scanner)
  → match score (resume.json + rules, already have matcher.py)
  → cover letter (drafter.py / LLM)
  → Playwright: open vacancy → click [data-qa="..."] → fill letter → submit
  → handle: employer questions, tests, captcha, mandatory letter modal → skip or queue
  → log to job_applications SQLite
  → Telegram: /approve apply <id> BEFORE send (semi-auto gate)
```

### Auth / session

1. **Playwright `storageState`** — один ручной login → `session.json` (cookies + localStorage).  
   Docs: [playwright auth](https://playwright.help/docs/auth)
2. **Persistent context** — `userDataDir` как отдельный профиль (`~/.personal-stack/hh-browser/`).
3. **CDP attach** — запуск реального Яндекс.Браузера/Chrome, `connect_over_cdp('http://localhost:9222')`.  
   Пример подхода: [Habr 1044588 hh-agent](https://habr.com/ru/articles/1044588/) — пароль вводит человек, скрипт не хранит.
4. **Cookie import** — как Habr Career сейчас; хуже для HH (короткий TTL, antifraud).

### Anti-detect (если на VPS)

- **RU residential IP** обязателен (NL VPS = red flag; у нас уже 403 на api.hh.ru).
- Не голый `headless=True` — patched Chromium, Xvfb, или headed на desktop user.
- Jitter 2–8 с между действиями, Bezier mouse, scroll.
- Лимит **≤200 откликов/сутки** (HH), практично **10–30** для semi-auto.
- Один аккаунт = один fingerprint profile.

### Селекторы HH

- Стабильнее всего `[data-qa="..."]` (vacancy-serp, response, и т.д.).
- Обработка: snackbar «Отклик отправлен», редирект на тест работодателя → skip.

---

## Open-source reference (можно заимствовать, не fork целиком)

| Repo | Stack | Что умеет |
|------|-------|-----------|
| [Steev193/hh-ru-apply](https://github.com/Steev193/hh-ru-apply) | Node + Playwright | login profile, harvest LLM, fill letter, apply chat |
| [iraguzov/hh-mcp-server](https://github.com/iraguzov/hh-mcp-server) | Playwright MCP | search, get resumes, apply_to_vacancy |
| Habr DIY | Python Playwright sync | serp cards, click respond, skip modals |

---

## Официальные «легальные» куски HH

- **@hh_rabota_bot** (Telegram): резюме, поиск, **поднять резюме в поиске** (раз в 4ч).  
  [База знаний HH](https://feedback.hh.ru/knowledge-base/article/0033744)  
  Не автоотклики, но **поднятие даты** без RPA — стоит проверить API бота vs web.
- Публичный **GET /vacancies** — поиск без токена (у нас в scanner; 403 с NL).

---

## Habr Career

- Нет публичного API профиля.
- Тот же Playwright + `HABR_SESSION_COOKIE` или persistent profile.
- Edit profile URL → fill about/skills → save.
- Задача в backlog: **JH-14**.

---

## LinkedIn

- Profile write API закрыт для физлиц.
- Варианты: PDF upload reminder (текущий), или Playwright на **linkedin.com** (высокий ban risk, частые UI changes).
- Низкий приоритет для RPA.

---

## Варианты для personal-stack (когда решим)

### A. Semi-auto RPA (рекомендуется)

- Orchestrator module `job_hunt/hh_browser.py` (Playwright).
- Auth: **CDP на домашнем ПК** или RU VPS + один раз login в headed browser.
- Flow: scanner → top leads → `/cover` → user `/approve apply <id>` → browser sends.
- Resume sync: edit resume page + «поднять» (или @hh_rabota_bot для lift only).
- Gate: никогда mass-apply без approve; daily cap в env.

### B. Desktop helper (Sofi-like)

- Electron/Tauri app у пользователя в РФ — браузер локально, агент на VPS только шлёт задачи по Telegram.
- Максимальный anti-detect, сложнее в разработке.

### C. Подписаться на Sofi / JobTurbo / podustal

- $/мес, не наш код, но работает сейчас.
- Не интегрируется с `resume.json` на сайте без ручного дубля.

### D. Только digest + @hh_rabota_bot

- Минимум риска; отклики руками с `/cover`.

---

## Риски (явно)

- Нарушение ToS HH → предупреждение / бан аккаунта.
- Хранение `storageState` в `secrets/` — утечка = полный доступ к HH.
- Captcha / employer tests — нужен human-in-the-loop.
- Селекторы ломаются при редизайне — нужен мониторинг + `codegen`.

---

## Suggested backlog (when user returns)

- **JH-16** HH Playwright apply (semi-auto, `/approve apply`)
- **JH-17** HH resume edit + publish via browser
- **JH-18** RU proxy / run browser on user machine via CDP
- **JH-19** Evaluate @hh_rabota_bot for resume lift API
- **JH-14** Habr Playwright profile (unchanged)

---

## Decision log

| Date | Note |
|------|------|
| 2026-06-23 | User: research Sofi-style automation; decide later |
| 2026-06-23 | Confirmed: post-API = browser RPA, not OAuth |
