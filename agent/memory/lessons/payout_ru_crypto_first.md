# Payout constraints (RU) — crypto wallet as north star

**Decision date:** 2026-06-23  
**Owner:** user (Максим, резидент РФ)

## Context

- **Gumroad / Lemon Squeezy / Paddle** — payout через Stripe/PayPal; для резидента РФ **непригодны** без зарубежного банка/entity.
- **PayPal / Stripe** у пользователя **нет** и из РФ не подключить для вывода.
- **Стартового капитала для крипто-трейдинга (A1/A2 live) нет** — до появления средств на кошельке live-торговля **не предлагать**.

## North star для income lanes

Любой lane считается **жизнеспособным**, если в итоге может **пополнить operational crypto wallet** (USDT/USDC на Bybit или on-chain — см. `secrets/.env.finance` / `YOUR_WALLET_ADDRESS`) через **auto или semi-auto** цикл:

| Lane | Semi-auto? | Путь в кошелёк | Статус |
|------|------------|----------------|--------|
| **A7 Bug bounty** | Да — orchestrator hunt + draft; user `/approve bounty` | **Immunefi / HackenProof** → USDC/USDT; HackerOne — проверить crypto payout в настройках аккаунта | **Primary focus** |
| **A4 Digital product** | Да — bundle + webhook | **Свой сайт + NOWPayments/Cryptomus** → USDT; не Gumroad | Background, после IB-16 |
| **A5 Affiliate** | Да — посты | Часто crypto payout у бирж (Bybit ref) — медленно, фон | Background |
| **A1 Azuro / A2 CEX live** | Auto после setup | Reinvest с кошелька | **Deferred** — нет seed capital |
| **A8 Salary / freelance** | Нет (ручной труд) | Рубли → обмен → USDT вручную | M3, не автonomía |

## Agent rules

1. **Не предлагать** Gumroad/Lemon как блокер A4 — предлагать **crypto checkout** или Telegram/manual USDT.
2. **Не предлагать** `FINANCE_LIVE=true` и деплой капитала в grid/Azuro, пока user явно не пополнил кошелёк и не дал approve.
3. **Paper scan** (Azuro/CEX) — опционально в логе, **не тратить daily cycle** на finance backlog, если есть открытые bounty tasks.
4. Логировать bounty payouts: `python3 -m finance.bounty_payout --net-usd <net> --platform immunefi --report-id <id>`.
5. Искать **новые площадки** с crypto payout и web/JS scope — каталог: `agent/memory/bounty_platforms.md`, backlog: `agent/tasks/bounty_backlog.md`.

## Related

- `agent/memory/income_plan.md` — обновлённый portfolio
- `agent/memory/products/agent-starter.md` — delivery без Gumroad
