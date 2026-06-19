# CEX grid trading: как настроить сетку на Bybit без ручных ордеров

> **Draft skeleton (A5 affiliate).** Замените `YOUR_AFFILIATE_ID` на реальные ссылки перед публикацией.

Grid trading на CEX — один из немногих **полностью API-driven** способов зарабатывать на волатильности без prediction markets. После paper-фазы на Azuro я переключил primary lane на **A2 CEX grid** — boring, но автономно.

## Что такое grid trading

**Grid** — сетка лимитных ордеров buy/sell в заданном ценовом диапазоне. Когда цена колеблется, бот покупает ниже и продаёт выше, фиксируя спред минус комиссии.

| Параметр | Рекомендация для старта |
|----------|-------------------------|
| Пара | BTC/USDT или ETH/USDT (ликвидность) |
| Диапазон | ±5–8% от текущей цены |
| Уровни | 5–10 (arithmetic grid) |
| Размер на уровень | $25–50 (paper first) |

<!-- TODO: скриншот grid preview из finance/grid_calculator -->

## Почему Bybit (NL-friendly)

- Spot + API без geo-block с NL VPS (в отличие от Polymarket)
- Низкие maker fees при grid (важно: fees съедают edge на малом капитале)
- Unified account для spot grid bots

**Affiliate:** [Bybit — регистрация](https://www.bybit.com/invite?ref=YOUR_AFFILIATE_ID) *(заменить ref)*

## Paper → live workflow

1. **Read-only scan** — `cex_client.py` возвращает top pairs по объёму.
2. **Grid calculator** — `grid_calculator.py` считает levels без live orders.
3. **7 дней paper** — логируем exposure, не включаем `FINANCE_LIVE`.
4. **Risk caps** — `MAX_TRADE_USD≤50`, `DAILY_STOP_LOSS_USD≤75`.

```text
daily scan → filter (liquidity, drift) → grid preview → JSON proposal → risk engine
```

## Когда grid не работает

- **Trending market** — односторонний тренд выбивает сетку из диапазона.
- **Низкий капитал** — комиссии > спред на $100 bankroll.
- **Высокая корреляция** — BTC+ETH+SOL grids одновременно = один риск.

## VPS для бота

Grid bot живёт на том же VPS, что и agent stack — systemd + cron, без облачных «trading bot SaaS».

**Affiliate (hosting):** [Hetzner Cloud](https://hetzner.cloud/?ref=YOUR_AFFILIATE_ID) · [DigitalOcean](https://www.digitalocean.com/?refcode=YOUR_AFFILIATE_ID)

<!-- TODO: добавить реальные affiliate IDs в secrets, не в git -->

## Связанные посты

- [Self-hosted agent stack](/blog/self-hosted-agent-stack) — orchestrator + finance scan
- *(TODO)* Azuro paper rules — почему NO-GO для live

## Disclosure

Пост содержит affiliate-ссылки. Это не финансовый совет — только описание моего paper/live workflow. DYOR.

---

*Связаться: [Telegram](https://t.me/makusimu_san) · [GitHub](https://github.com/mpeshehonov)*
