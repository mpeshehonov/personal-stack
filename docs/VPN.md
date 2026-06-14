# VPN operations

VPN runs in **separate Docker Compose projects** from the site stack. Site deploy must never restart VPN containers.

## Compose projects

| Project | Path | Containers |
|---------|------|------------|
| `hysteria2` | `vpn/hysteria2/` | `hysteria2-nl-36712`, `hysteria2-nl-8443`, `hy2-subscription` |
| `xray-reality` | `vpn/xray-reality/` | `xray-reality-vless` |
| `personal-stack` | repo root | `site`, `caddy`, `redis` only |

All VPN services use `restart: unless-stopped`.

## Site deploy (safe)

`scripts/deploy-from-git.sh` and `scripts/redeploy-site.sh` only touch site services:

```bash
docker compose build site
docker compose up -d site caddy
```

They do **not** run `docker compose up -d` on the full stack and do **not** call `scripts/deploy-vpn.sh`.

After deploy, `vpn/ensure-up.sh` verifies VPN containers are running and starts them only if down.

## VPN deploy (manual only)

Use `scripts/deploy-vpn.sh` when changing VPN configs, ports, or sysctl. This script **will** recreate VPN containers (`--force-recreate`) and briefly interrupt connections.

## Verify VPN survived a site deploy

```bash
# Before deploy — note StartedAt timestamps
docker inspect -f '{{.Name}} {{.State.StartedAt}}' \
  hysteria2-nl-36712 hysteria2-nl-8443 xray-reality-vless

./scripts/deploy-from-git.sh

# After deploy — StartedAt must be unchanged
docker inspect -f '{{.Name}} {{.State.StartedAt}}' \
  hysteria2-nl-36712 hysteria2-nl-8443 xray-reality-vless
```

Or run `./vpn/ensure-up.sh` — it prints running status and exits 0 when healthy.

## Split routing — RU sites without VPN

When VPN is on, Russian sites (`.ru`, `.su`, `.рф`, Yandex/VK/banks/gov) go **direct**. Everything else uses the tunnel.

| Resource | URL |
|----------|-----|
| Docs | `vpn/routing/README.md` |
| Happ link | `http://89.124.70.216:8888/routing/happ-ru-direct.link` |
| JSON profile | `http://89.124.70.216:8888/routing/happ-ru-direct.json` |

**Setup (Happ):** import subscription → open routing link from table above → verify with `2ip.ru` (real IP) vs `ifconfig.me` (NL server IP).

## Mobile data (РФ, «белые списки»)

На мобильном интернете **Hysteria2 (UDP/QUIC, порты 36712/8443) часто не работает** — оператор режет UDP вне whitelist.

| Сеть | Протокол | Почему |
|------|----------|--------|
| Wi‑Fi | Hysteria2 (Hy2) | UDP обычно проходит |
| Mobile 4G/5G | **Xray REALITY TCP :2053** | TCP под видом `yandex.ru`, не QUIC |

1. В Happ выберите профиль **Xray REALITY** (не Hy2) для мобильной сети — параметры в `vpn/xray-reality/WORKING.txt` на сервере.
2. Routing **RU-direct** оставьте включённым.
3. iPhone: VPN → Connect On Demand; Happ → Include all networks **ON**.

## После сна ноутбука (нет reconnect)

Hy2 (UDP) часто не восстанавливается после sleep.

- Happ: auto-reconnect; после wake — выкл VPN → 3 сек → вкл
- На mobile и после sleep предпочитайте **Xray TCP 2053**
- Сервер: Hy2 idle timeout 300s в `vpn/hysteria2/config*.yaml`; после правки — `scripts/deploy-vpn.sh`

**Edit whitelist:** add domains to `vpn/routing/ru-direct-sites.txt`, then:

```bash
bash /opt/personal-stack/vpn/scripts/build-happ-routing.sh
```

Redeploy subscription nginx only if needed: `cd vpn/hysteria2 && docker compose up -d hy2-subscription`.
