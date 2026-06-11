# Agent Memory Index

## Active Agent
- cursor_agent_id: stored in state.sqlite kv table
- model: auto

## Stack Paths
- Site: /opt/personal-stack/site
- Memory: /opt/personal-stack/agent/memory
- Secrets: /opt/personal-stack/secrets (never commit)

## Rules
1. Never submit bug bounty reports without Telegram approval
2. Never bypass Risk Engine for finance
3. Max 1-2 site improvements per day
4. Use scripts/redeploy-site.sh to restart site
5. Annual earning goal: $15,000 by 2026-12-31
6. **Git workflow:** все правки только через git — перед `/task` бот делает `git pull`; после задачи auto commit+push+deploy. Не оставлять правки только на сервере. Локальная разработка → push → deploy-from-git.sh

## VPN
- Primary: Hysteria2 UDP 36712 (+ Salamander obfs) — vpn/hysteria2/WORKING.txt
- Subscription: http://89.124.70.216:8888/sub.txt
- Fallback: VLESS Reality TCP 2053
- Site: HTTPS on 443/TCP (Caddy)
- **Site deploy is isolated from VPN** — use `docker compose up -d site caddy` only; VPN runs in separate compose projects (`hysteria2`, `xray-reality`). See docs/VPN.md. VPN changes: `scripts/deploy-vpn.sh` only (manual).

## Links
- Resume source: site/content/resume/resume.json
