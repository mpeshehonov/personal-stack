# VPN routing — RU direct bypass

Когда VPN включён, **русскоязычные сайты и `.ru` идут напрямую** (без туннеля). Остальной трафик — через прокси.

## Happ (iPhone / Android) — рекомендуется

1. Импортируйте / обновите подписку: `http://89.124.70.216:8888/sub.txt`  
   Роутинг **RU-direct** подтягивается сам (`happ://routing/onadd/…` в теле подписки).
2. В Happ: **Routing → RU-direct** должен стать активным после update (reconnect, если уже был коннект).
3. iPhone: Include all networks **ON**, Exclude local + APNS **ON**

Ручной импорт (если нужно): `http://89.124.70.216:8888/routing/happ-ru-direct.link`

### Что в белом списке

| Правило | Покрытие |
|---------|----------|
| `geosite:category-ru-all` | Yandex, VK, банки, гос, маркетплейсы, ТВ (~140 категорий из [ru-routing-dat](https://github.com/GrimbirdUsers/ru-routing-dat)) |
| `domain:ru` | Все домены в зоне `.ru` |
| `domain:su` | Зона `.su` |
| `domain:xn--p1ai` | Зона `.рф` |
| `domain:moscow` | Зона `.moscow` |
| `geoip:ru` | IP-адреса РФ |
| `ru-direct-sites.txt` | Доп. домены (vk.com, okko.tv и т.д.) |

**DNS:** для DIRECT — Yandex `77.88.8.8`, для прокси — Cloudflare `1.1.1.1`.

## Обновление профиля

После правок в `ru-direct-sites.txt`:

```bash
bash /opt/personal-stack/vpn/scripts/build-happ-routing.sh
```

Файлы копируются в `vpn/hysteria2/subscription/routing/` (раздаёт nginx на `:8888`).

## v2rayNG / Nekoray / Streisand

1. Скачайте geosite/geoip: [ru-routing-dat releases](https://github.com/GrimbirdUsers/ru-routing-dat)
2. Шаблон клиента: `xray-client-ru-direct.json.template` — подставьте UUID/ключи из `WORKING.txt`
3. Правила routing: DIRECT для `geosite:category-ru-all`, `domain:ru`, `geoip:ru`

## Файлы

| Файл | Назначение |
|------|------------|
| `happ-ru-direct.base.json` | Базовый профиль Happ |
| `ru-direct-sites.txt` | Доп. домены (редактируемый список) |
| `happ-ru-direct.json` | Собранный профиль |
| `happ-ru-direct.link` | `happ://routing/onadd/...` |
| `scripts/build-happ-routing.sh` | Сборка профиля |

## Проверка

1. VPN **включён**
2. Открыть `https://2ip.ru` — должен показать **ваш реальный IP** (не NL)
3. Открыть `https://ifconfig.me` — должен показать **IP сервера NL**

Если `.ru` всё ещё через VPN — обновите geosite в Happ (Settings → Update geo files) и переактивируйте профиль.
