# VPN operations

VPN runs in **separate Docker Compose** from the site stack. Site deploy must never restart VPN containers.

## Compose project

| Project | Path | Containers |
|---------|------|------------|
| `hysteria2` | `vpn/hysteria2/` | `hysteria2-nl-36712`, `hy2-subscription` |
| `personal-stack` | repo root | `site`, `caddy`, `redis` only |

All VPN services use `restart: unless-stopped`. **Hysteria2 only** — one profile **Yandex-HY2** on UDP **36712**.

## Port

| Port | Use |
|------|-----|
| 36712 | **Yandex-HY2** — Wi‑Fi and mobile (Salamander + yandex masquerade) |
| 8888/tcp | Happ subscription (`sub.txt`) |

TCP 443 is Caddy (site). Hy2 uses UDP 36712 only.

## Happ setup

1. Import subscription: `http://89.124.70.216:8888/sub.txt`
2. Routing RU-direct: `http://89.124.70.216:8888/routing/happ-ru-direct.link`
3. Single node: **Yandex-HY2**
4. Happ settings (via subscription headers):
   - Include all networks **ON**
   - Exclude local + APNS **ON**
   - Subscription ping on open **ON**

## Server tuning (mobile)

- `ping: 5s` — server keepalive for NAT
- `maxIdleTimeout` / `udpIdleTimeout`: **30s**
- `disablePathMTUDiscovery: false`
- Salamander obfs + yandex.ru masquerade

If mobile QUIC still drops, the carrier may be throttling UDP — consider TCP fallback (VLESS Reality) separately.

## Rebuild subscription

```bash
bash /opt/personal-stack/vpn/scripts/build-hy2-subscription.sh
```

## VPN deploy (manual)

`scripts/deploy-vpn.sh` — recreates VPN containers (~30s disconnect).

## Verify

- VPN ON, routing ON
- `https://ifconfig.me` → `89.124.70.216`
