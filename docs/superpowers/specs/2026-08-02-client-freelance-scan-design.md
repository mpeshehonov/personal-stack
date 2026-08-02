# CLIENT Freelance Scan MVP (2026-08-02)

## Goal

Бесплатный поиск клиентских заказов (не FT-вакансий) с результатом в `/brief` и `/clients` за 1 день.

## Decision

Не FL.ru/Kwork scrape (антибот, без подписки).  
**Источник:** публичные TG-превью `t.me/s/…`, в первую очередь `@freelansim_ru` (дайджесты Хабр Фриланс) + `@job_webdev`.

## Flow

1. `opportunity/client_scan.py` тянет превью каналов  
2. Парсит пункты дайджеста → отдельные заказы с URL `u.habr.com`  
3. Скорит FE-fit (React/Next/TS/кабинет), режет дешёвые/backend/ботов  
4. `upsert_seed` → `opportunities` type=`CLIENT`, `analysis.kind=freelance_order`  
5. Хук в `after_scan_hook` / `ensure_all_opportunities`  
6. `/clients` — ручной скан; `/brief` показывает до 5 CLIENT (orders first)

## Network

`network_pitch` в `opportunity_profile.json` — готовый текст для тёплых сообщений знакомым.

## Non-goals (сейчас)

- Платные агрегаторы / Hirify Plus  
- Авто-отклик на Хабре  
- Upwork  

## Success

- `/clients` возвращает десятки FE-заказов без оплаты  
- В brief есть карточки со ссылкой «Открыть»  
- Итерации: новые каналы, жёстче фильтр бюджета, шаблон отклика на заказ  
