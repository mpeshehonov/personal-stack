# CLIENT Freelance Scan MVP (2026-08-02)

## Goal

Бесплатный поиск клиентских заказов (не FT-вакансий) с результатом в `/brief` и `/clients` за 1 день.

## Decision (updated after Habr Freelance shutdown)

**Habr Freelance закрыт** — `freelance.habr.com` / `u.habr.com` / `@freelansim_ru` запрещены.

Живые бесплатные источники:
1. **FL.ru** `/projects/` — карточка валидируется (`Откликнуться` + дата публикации)
2. **TG** `@job_webdev`, `@it_zakazy`, `@projects_fl` — только посты младше **72ч**, ссылка на Kwork/FL предпочтительнее голого t.me
3. Kwork want pages — проверка `status:active` / страница want

Hard gates: freshness ≤72h, не dead URL, FE-сигнал, бюджет не копеечный.

## Flow

1. `purge_dead_client_opportunities()` архивирует CLIENT с habr-ссылками  
2. Скан FL + TG → validate → `upsert_seed` (`kind=freelance_order`)  
3. `/clients` и daily `after_scan_hook`

## Success

- Ссылки открываются и принимают отклик  
- Нет карточек на закрытый Хабр Фриланс  
- В brief только свежие заказы  
