# VPN operations

VPN runs in **separate Docker Compose** from the site stack. Site deploy must never restart VPN containers.

## Compose project

| Project | Path | Containers |
|---------|------|------------|
| `hysteria2` | `vpn/hysteria2/` | `hysteria2-nl-443`, `hysteria2-nl-36712`, `hysteria2-nl-8443`, `hy2-subscription` |
| `personal-stack` | repo root | `site`, `caddy`, `redis` only |

All VPN services use `restart: unless-stopped`. **Hysteria2 only** — VLESS/Xray removed.

## Ports (UDP)

| Port | Use |
|------|-----|
| **443** | Primary for mobile (QUIC looks like HTTPS) |
| 36712 | **Yandex-HY2** — Wi‑Fi / основной |
| 8443 | **Yandex-HY2-8443** — запасной |

TCP 443 is Caddy (site). UDP 443 is Hy2 — no conflict.

## Happ setup

1. Import subscription: `http://89.124.70.216:8888/sub.txt`
2. Routing RU-direct: `http://89.124.70.216:8888/routing/happ-ru-direct.link`
3. On **mobile**: prefer node **Yandex-HY2-mobile** (UDP 443); Wi‑Fi — **Yandex-HY2** (36712)
4. Happ settings (enabled via subscription headers):
   - Include all networks **ON**
   - Exclude local + APNS **ON**
   - Subscription ping on open **ON** (faster reconnect after sleep)

## After sleep / idle

Server idle timeout: **600s**. Client: re-import `sub.txt` after deploy; toggle VPN if stuck.

## Mobile (РФ)

Operators may throttle non-whitelist UDP. **Port 443 UDP** + Salamander obfs + yandex masquerade gives the best Hy2 success rate. If one port fails, try 8443 or 36712 in Happ.

## Rebuild subscription

```bash
bash /opt/personal-stack/vpn/scripts/build-hy2-subscription.sh
```

After `ru-direct-sites.txt` changes:

```bash
bash /opt/personal-stack/vpn/scripts/build-happ-routing.sh
```

## VPN deploy (manual)

`scripts/deploy-vpn.sh` — recreates VPN containers (~30s disconnect).

## Site deploy (safe)

`scripts/deploy-from-git.sh` — site + caddy only; `vpn/ensure-up.sh` verifies VPN.

## Verify

- VPN ON, routing ON
- `https://2ip.ru` → real IP
- `https://ifconfig.me` → `89.124.70.216`
