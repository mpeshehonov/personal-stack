# Agent Memory Index

## Harness
- Map: `agent/instructions.md`
- Daily: `agent/tasks/daily_prompt.md` + `agent/orchestrator/daily_validator.py`
- Skills: `agent/skills/resume-copy/`, `cover-letter/`, `resume-review-*`

## Active Agent
- cursor_agent_id: stored in state.sqlite kv table
- model: auto
- **Mode: career hunter** (income/bounty paused 2026-07-20)

## Stack Paths
- Site: /opt/personal-stack/site
- Memory: /opt/personal-stack/agent/memory
- Secrets: /opt/personal-stack/secrets (never commit)

## Rules
1. **North star:** сильные вакансии/проекты + самообучение источников (`job_hunt/`, `/jobs`, `/sources`)
2. Income/bounty/trading: **paused** — не предлагать hunt/live finance/Gumroad
3. Сайт не улучшать автономно: copy/design/feature только с пользователем; daily — health/redeploy если лежит
4. Use scripts/redeploy-site.sh to restart site
5. **Git workflow:** правки через git — bot `git pull` перед `/task`; после — commit+push+deploy
6. Resume public copy: HR red-flag pass — `lessons/resume_no_hr_red_flags.md`

## VPN
- Primary: Hysteria2 UDP **443** (mobile) + 8443 + 36712 — `vpn/hysteria2/WORKING.txt`
- Subscription: http://89.124.70.216:8888/sub.txt
- Site: HTTPS on 443/TCP (Caddy); Hy2 uses 443/UDP

## Links
- Resume: site/content/resume/ + site/lib/resume-data.ts
- Job hunt: `agent/tasks/job_hunt_backlog.md`, `docs/JOB-HUNT-AUTH-SETUP.md`
- Career strategy: `docs/career-growth-system.md` + backlog + schema
- Lessons: `resume_sells_in_15_seconds.md`, `resume_no_hr_red_flags.md`
