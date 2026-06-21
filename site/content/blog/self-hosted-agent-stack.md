# Self-hosted agent stack: как я автоматизирую рутину

За последний год я собрал **self-hosted стек** для AI-агентов и ежедневных автоматизаций: VPS, Docker, Telegram-бот и Cursor SDK — без привязки к облачным «агентным» подпискам и с полным контролем над данными.

## Зачем self-hosted

**Контроль данных.** Промпты, логи, finance-сигналы и черновики bounty остаются на своём сервере в SQLite и markdown-памяти — не в чужом SaaS.

**Предсказуемые расходы.** Фиксированный VPS + API Cursor вместо pay-per-seat agent platforms.

**Свой CI/CD-контур.** Сайт, агент и VPN живут в одном репозитории; деплой — `git pull` и systemd, без GitHub Actions с секретами в workflow.

## Архитектура

```text
Telegram (/ask, /task, /bounty)
        │
        ▼
  telegram-bot ──► Cursor SDK (local bridge)
        │
        ▼
 agent-orchestrator ──► daily cycle
        │                    │
        ├── bounty/scanner   ├── finance executor
        ├── job_hunt         ├── site deploy
        └── memory commit    └── Telegram report
```

| Слой | Инструмент |
|------|------------|
| VPS | Ubuntu, systemd |
| Сайт | Next.js 15, standalone, Caddy |
| Агенты | Cursor SDK + Python orchestrator |
| Память | `agent/memory/` + SQLite state |
| Уведомления | Telegram Rich Messages |
| VPN | Hysteria2 + Xray REALITY (отдельный compose) |

## Ежедневный цикл

Каждое утро orchestrator:

1. Проверяет health (CPU, RAM, сайт, Docker).
2. Запускает **daily-агента** с harness: plan → bounded work → validate → log.
3. Прогоняет finance scan (Azuro/CEX paper), bounty semi-auto, job hunt.
4. Коммитит `agent/memory/`, шлёт отчёт в Telegram.

Агент не «магически зарабатывает» — он работает по **lanes** из income plan: paper-trading, сигналы, контент. Рискованные действия (live trades, bounty submit) — только после `/approve` в боте.

## Bug bounty semi-auto

Отдельный pipeline: purge слабых драфтов → 4 фазы research (scope → recon → hunt → report) → auto-QA → reviewer → pending draft. Submit на HackerOne — только после твоего `/approve bounty`.

Это снимает рутину «проверь GHSA и накинь hint», но не заменяет реальный PoC — агент обязан принести curl и submit-ready report.

## Telegram-бот

- `/ask` — read-only вопрос со стримингом
- `/task` — правки кода + auto deploy
- `/bounty hunt` — deep research в фоне (бот не блокируется)
- `/status` — health + фоновые задачи

Долгие job'ы идут в `asyncio.create_task`; Cursor SDK сериализуется через session lock — иначе bridge падает с Connection refused.

## Что я бы сделал иначе с нуля

1. **Harness с первого дня** — plan artifact, validators, approval gates (см. [agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices)).
2. **Skills по lanes** — income, bounty, site — progressive disclosure вместо одного простынного prompt.
3. **Paper trading 7 дней** до любого live finance — kill criteria в коде, не в голове.

## Стек в цифрах

- ~15 systemd/cron триггеров
- 4 фазы bounty research на программу
- 2 VPN протокола (Hy2 для Wi‑Fi, Xray REALITY TCP для mobile)
- 0 облачных agent subscriptions

## Что дальше

- Milestone M1: $1k autonomous net к сентябрю 2026
- Job hunt autopilot с HH API
- [CEX grid trading на Bybit](/blog/cex-grid-trading-bybit) — primary finance lane после Azuro NO-GO

---

*Связаться: [Telegram](https://t.me/makusimu_san) · [GitHub](https://github.com/mpeshehonov) · [Сайт](https://mpeshekhonov.ru)*
