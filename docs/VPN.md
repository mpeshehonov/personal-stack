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
