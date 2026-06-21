# CEX grid trading: как настроить сетку на Bybit без ручных ордеров

Grid trading на CEX — один из немногих **полностью API-driven** способов зарабатывать на волатильности без prediction markets. После paper-фазы на Azuro я переключил primary lane на **A2 CEX grid** — boring, но автономно.

## Что такое grid trading

**Grid** — сетка лимитных ордеров buy/sell в заданном ценовом диапазоне. Когда цена колеблется, бот покупает ниже и продаёт выше, фиксируя спред минус комиссии.

| Параметр | Рекомендация для старта |
|----------|-------------------------|
| Пара | BTC/USDT или ETH/USDT (ликвидность) |
| Диапазон | ±5–8% от текущей цены |
| Уровни | 5–10 (arithmetic grid) |
| Размер на уровень | $25–50 (paper first) |

## Пример grid preview (paper scan)

Из `grid_calculator.py` на текущем скане (BTCUSDT, $300 capital, 5 levels, 10% span):

```text
BTCUSDT grid: $61,042 – $67,468 (anchor ~$64,255)
Per level: ~$60 · arithmetic · read-only preview
```

Это **не** live-ордера — только preview перед approval и `FINANCE_LIVE`.

## Почему Bybit (NL-friendly)

- Spot + API без geo-block с NL VPS (в отличие от Polymarket)
- Низкие maker fees при grid (важно: fees съедают edge на малом капитале)
- Unified account для spot grid bots

[Bybit — регистрация](https://www.bybit.com/)

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

- [Hetzner Cloud](https://www.hetzner.com/cloud)
- [DigitalOcean](https://www.digitalocean.com/)

## Связанные посты

- [Self-hosted agent stack](/blog/self-hosted-agent-stack) — orchestrator + finance scan

## Disclosure

Ссылки на сервисы — без affiliate ref (можно добавить позже). Это не финансовый совет — только описание моего paper/live workflow. DYOR.

---

*Связаться: [Telegram](https://t.me/makusimu_san) · [GitHub](https://github.com/mpeshehonov)*
