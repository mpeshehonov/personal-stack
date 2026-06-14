# Xray REALITY — Happ / v2rayNG

Отдельный профиль от Hysteria2. **Для mobile 4G/5G в РФ** — предпочитай REALITY (TCP), не Hy2 (UDP).

## Где взять строку

На сервере:

```bash
cat /opt/personal-stack/vpn/xray-reality/WORKING.txt
```

## Happ (iOS / Android)

1. **Добавить узел:** Happ → «+» → **Import from clipboard** (или «Добавить вручную»).
2. Вставить **VLESS URI** (запасной порт 2053 — для mobile):

```
vless://UUID@89.124.70.216:2053?encryption=none&security=reality&sni=yandex.ru&fp=chrome&pbk=PUBLIC_KEY&sid=SHORT_ID&type=tcp&headerType=none#Reality-NL-2053
```

3. Подставь `UUID`, `PUBLIC_KEY`, `SHORT_ID` из `WORKING.txt`.
4. **Routing:** импортируй RU-direct (`.ru` напрямую):
   - `http://89.124.70.216:8888/routing/happ-ru-direct.link`
5. Подписка Hy2 (`sub.txt`) и узел Xray — **два разных импорта**. Можно держать оба; на mobile выбирай Reality-NL-2053.

### Основной (Vision, 443)

Если 443 свободен и не режется оператором:

```
vless://UUID@89.124.70.216:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=yandex.ru&fp=chrome&pbk=PUBLIC_KEY&sid=SHORT_ID&type=tcp&headerType=none#Reality-NL-443
```

## Проверка

- VPN **ON**, routing RU-direct **ON**
- `https://2ip.ru` → ваш реальный IP
- `https://ifconfig.me` → IP сервера NL (89.124.70.216)

## Не путать

| | Hysteria2 | Xray REALITY |
|---|-----------|--------------|
| Транспорт | UDP/QUIC | TCP |
| Mobile РФ | часто блок | обычно работает |
| Импорт | subscription `sub.txt` | VLESS URI вручную |

См. также `docs/VPN.md`.
