# Agent Memory Index

## Harness
- Map: `agent/instructions.md`
- Daily: `agent/tasks/daily_prompt.md` + `agent/orchestrator/daily_validator.py`
- Skills: `agent/skills/income-harness/`, `agent/skills/bounty-harness/`

## Active Agent
- cursor_agent_id: stored in state.sqlite kv table
- model: auto

## Stack Paths
- Site: /opt/personal-stack/site
- Memory: /opt/personal-stack/agent/memory
- Secrets: /opt/personal-stack/secrets (never commit)

## Rules
1. Bug bounty: orchestrator создаёт **только submit-ready отчёты**; submit **только** после `/approve bounty <id>` (авто на HackerOne если настроено)
2. Never bypass Risk Engine for finance
3. Сайт не улучшать автономно: copy/design/feature изменения только вручную с пользователем; daily может делать только health/redeploy если сайт лежит
4. Use scripts/redeploy-site.sh to restart site
5. Income plan: M1 $1,000 autonomous by 2026-09-30 → M3 $15,000 by 2026-12-31 — see `agent/memory/income_plan.md`
6. **Git workflow:** все правки только через git — перед `/task` бот делает `git pull`; после задачи auto commit+push+deploy. Не оставлять правки только на сервере. Локальная разработка → push → deploy-from-git.sh

## VPN
- Primary: Hysteria2 UDP **443** (mobile) + 8443 + 36712 — `vpn/hysteria2/WORKING.txt`
- Subscription: http://89.124.70.216:8888/sub.txt (rebuild: `vpn/scripts/build-hy2-subscription.sh`)
- **Split routing (RU direct):** http://89.124.70.216:8888/routing/happ-ru-direct.link
- Site: HTTPS on 443/TCP (Caddy); Hy2 uses 443/UDP

## Links
- Resume source: site/content/resume/resume.json
