# Job Hunt — авторизации и sync резюме

Источник правды: `site/content/resume/resume.json` (+ `resume.md` для «О себе»).

> **Важно:** с **15 декабря 2025** HeadHunter **закрыл API для соискателей** (OAuth, редактирование резюме, publish).  
> Подробнее: `agent/memory/lessons/hh_applicant_api_closed.md`

---

## Что можно автоматизировать (2026)

| Площадка | Auto-push | Что делаем |
|----------|-----------|------------|
| **HH.ru** | ❌ API мёртв | `/jobs hh-digest` — текст для **ручной** вставки; опционально JH-16 Playwright+cookie |
| **Habr Career** | ⏳ JH-14 | Cookie → verify сейчас; Playwright push позже |
| **LinkedIn** | ❌ нет API | Cookie verify + напоминание загрузить PDF с сайта |
| **Поиск вакансий HH** | ✅ публичный GET | `GET /vacancies` без токена (может 403 с NL VPS → Habr/Hirify) |

---

## Быстрый старт

```bash
cp secrets/.env.jobhunt.template secrets/.env.jobhunt
chmod 600 secrets/.env.jobhunt
# JOBHUNT_RESUME_SYNC_ENABLED=true
# Habr cookie — см. ниже
cd agent && python3 ../scripts/check-job-hunt-auth.py auth
```

Telegram:

- `/jobs hh-digest` — блоки для копипаста в HH
- `/jobs auth` — Habr + LinkedIn
- `/jobs sync` — diff с site
- `/approve resume habr` — push Habr (после JH-14)

**Не настраивай** `HH_CLIENT_ID` / OAuth — бесполезно для соискателя.

---

## 1. HeadHunter — digest (рекомендуется)

1. Обнови `resume.json` на сайте → deploy
2. `/jobs hh-digest` в Telegram (или `python3 ../scripts/check-job-hunt-auth.py hh-digest`)
3. Открой https://hh.ru/applicant/resumes → редактировать
4. Вставь: должность, «О себе», навыки
5. Нажми «Поднять в поиске» в UI

Сопроводительные к вакансиям: `/cover <id>` — как раньше.

### Опционально: browser automation (JH-16, риск ToS)

Playwright + session cookie с домашнего браузера — **только** после явного решения и `/approve`.  
Не реализовано; не регистрируй приложение на dev.hh.ru для соискателя.

---

## 2. Habr Career (приоритет для auto)

Публичного API нет. Нужна **session cookie**.

1. https://career.habr.com → логин
2. DevTools → Cookies → `career.habr.com`
3. В `secrets/.env.jobhunt`:

```bash
JOBHUNT_RESUME_SYNC_ENABLED=true
HABR_SESSION_COOKIE=_habr_career_session=XXXX
HABR_PROFILE_SLUG=твой-slug   # из URL /users/SLUG
```

4. `/jobs auth` → ✅ habr

Push профиля — задача **JH-14** (Playwright).

---

## 3. LinkedIn (опционально)

Auto-write через API недоступен. Cookie только для verify + PDF reminder.

```bash
LINKEDIN_SYNC_ENABLED=true
LINKEDIN_LI_AT=...
LINKEDIN_JSESSIONID=...
```

PDF: https://mpeshekhonov.ru/ru/resume/download

---

## 4. Общие флаги

```bash
JOBHUNT_RESUME_SYNC_ENABLED=true
JOBHUNT_RESUME_AUTO_SYNC=false
```

---

## 5. Checklist

- [ ] `secrets/.env.jobhunt` из template
- [ ] `JOBHUNT_RESUME_SYNC_ENABLED=true`
- [ ] ~~HH OAuth~~ — **не нужен**
- [ ] Habr: cookie + profile slug
- [ ] (опц.) LinkedIn: li_at
- [ ] `/jobs hh-digest` после правок resume.json
- [ ] `/jobs auth` — Habr ✅

---

## Related

- `agent/memory/research/job_automation_rpa_2026.md` — **RPA / Sofi-style** (Playwright, post-API)
- `agent/job_hunt/hh_digest.py`
- `agent/tasks/job_hunt_backlog.md` — JH-14 (Habr), JH-16+ (HH browser)
- `docs/superpowers/specs/2026-06-13-job-hunt-autopilot-design.md`
