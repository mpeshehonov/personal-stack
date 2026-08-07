# VPN operations

VPN runs in **separate Docker Compose** from the site stack. Site deploy must never restart VPN containers.

## Compose project

| Project | Path | Containers |
|---------|------|------------|
| `hysteria2` | `vpn/hysteria2/` | `hysteria2-nl-8443`, `hysteria2-nl-36712`, `hy2-subscription` |
| `personal-stack` | repo root | `site`, `caddy`, `redis` only |

All VPN services use `restart: unless-stopped`. **Hysteria2 only** — Happ subscription, no VLESS.

## Ports

| Port | Use |
|------|-----|
| 8443/udp | **Yandex-HY2-8443** — primary for mobile / whitelist |
| 36712/udp | **Yandex-HY2-36712** — backup (Wi‑Fi) |
| 8888/tcp | Happ subscription (`sub.txt`) |

TCP 443 is Caddy (site). Hy2 uses UDP only.

## Happ setup

1. Import subscription: `http://89.124.70.216:8888/sub.txt`
2. Update subscription in Happ with **Update routing** ON → reconnect.
   Delivery: HTTP header `routing:` + `happ://routing/onadd/…` in body (profile name `RU-direct`, `LastUpdated` bumps each rebuild).
3. Nodes: **Yandex-HY2-36712** (Wi‑Fi), **Yandex-HY2-8443** (mobile / whitelist)
4. Happ settings (via subscription):
   - Include all networks **ON**
   - Exclude local + APNS **ON**

If routing still empty: delete the subscription → re-import `sub.txt` fresh (old sub can ignore body routing). Manual link: `http://89.124.70.216:8888/routing/happ-ru-direct.link`

Happ does **not** support Amnezia protocol — use the Amnezia app for Amnezia configs.

## Server tuning (mobile)

- `maxIdleTimeout` / `udpIdleTimeout`: **120s** (Hysteria max; do not go below)
- Server `ping: 5s` — keepalive for mobile NAT

## Rebuild subscription

```bash
bash /opt/personal-stack/vpn/scripts/build-multi-subscription.sh
```

Rebuilds RU-direct profile + `sub.txt` (routing embedded) and reloads nginx on `:8888`.

Routing-only rebuild:

```bash
bash /opt/personal-stack/vpn/scripts/build-happ-routing.sh
```

## VPN deploy (manual)

`scripts/deploy-vpn.sh` — starts Hy2 containers and rebuilds subscription.

## Verify

```bash
bash /opt/personal-stack/vpn/hysteria2/verify-hy2.sh
```

- VPN ON, routing ON
- `https://ifconfig.me` → `89.124.70.216`
