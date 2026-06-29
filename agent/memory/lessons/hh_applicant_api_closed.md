# HH.ru applicant API closed (2025-12-15)

**Date:** 2025-12-15 (official) · recorded in stack 2026-06-23

## What closed

HeadHunter **закрыл API для соискателей** с 15 декабря 2025:

- OAuth applicant tokens (`dev.hh.ru` apps for job seekers)
- `GET /resumes/mine`, `PUT /resumes/:id`, `POST /resumes/:id/publish`
- Программные отклики и автообновление резюме через API

**Причина (официально):** борьба с ботами, массовыми откликами, утечками данных.

## What still works (for our stack)

| Feature | Status |
|---------|--------|
| **Поиск вакансий** `GET /api.hh.ru/vacancies` (без токена) | Может работать; с NL VPS часто **403** → fallback Habr/Hirify |
| **Сопроводительные** `/cover <id>` | OK — текст для ручной вставки |
| **Resume sync через API** | **Мёртв** — не настраивать OAuth |

## Replacement options (ranked)

1. **Digest (default, safe)** — агент собирает блоки из `resume.json` → Telegram «скопируй в HH вручную» (`/jobs hh-digest`)
2. **Browser session (JH-16, semi-auto)** — cookie + Playwright, только после `/approve resume hh`, риск ToS/бан
3. **Ручное** — PDF/сайт как источник правды

## Agent rules

- Не предлагать `HH_CLIENT_ID`, OAuth, `dev.hh.ru` для соискателя
- Не тратить backlog на `hh_resume.py` API client
- Vacancy scan: `JOBHUNT_HH_ENABLED` OK; при 403 — не чинить OAuth, использовать другие источники
- Resume push HH: digest или будущий Playwright (JH-16)

## Related

- `docs/JOB-HUNT-AUTH-SETUP.md`
- `agent/job_hunt/hh_digest.py`
