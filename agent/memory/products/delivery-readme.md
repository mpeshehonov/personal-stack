# Personal Stack Agent Starter — Buyer Bootstrap Guide

> Delivered with Gumroad purchase. Version: **0.2** (2026-06-22).

## What you get

A production-tested self-hosted stack:

- **Next.js 15** portfolio site (standalone Docker)
- **Python orchestrator** — daily cycle, validators, memory commit
- **Telegram bot** — `/task`, `/ask`, `/status`, approval gates
- **Finance harness** — multi-venue scan, risk engine, paper-first trading
- **Bounty pipeline** — draft-only until `/approve bounty`
- **Deploy scripts** — `deploy-from-git.sh`, `redeploy-site.sh`

## Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| VPS | 2 GB RAM, 1 vCPU | 4 GB RAM, 2 vCPU |
| OS | Ubuntu 22.04+ | Ubuntu 24.04 |
| Domain | HTTPS required | Caddy example included |
| API keys | Cursor, Telegram | Bybit/Azuro optional (paper default) |

## Quick start (2–4 hours)

### 1. Clone and secrets

```bash
git clone <your-private-repo-url> personal-stack
cd personal-stack
cp secrets/.env.example secrets/.env
# Edit secrets/.env — never commit this file
```

Required env vars:

- `CURSOR_API_KEY` — Cursor agent bridge
- `TELEGRAM_BOT_TOKEN` — bot from @BotFather
- `TELEGRAM_ALLOWED_USER_IDS` — your Telegram user ID

Optional (finance, disabled by default):

- `FINANCE_LIVE=false` — keep false until you explicitly enable
- `BYBIT_API_KEY` / `BYBIT_API_SECRET` — CEX grid lane

### 2. Bootstrap server

```bash
sudo ./scripts/bootstrap-server.sh   # systemd units, docker, caddy
./scripts/deploy-from-git.sh         # site + orchestrator
```

### 3. Verify health

```bash
curl -s https://your-domain/ru | head
systemctl status agent-orchestrator telegram-bot
```

Telegram: send `/status` — expect CPU/RAM/site health.

### 4. First daily cycle

```bash
systemctl start agent-orchestrator   # or wait for cron
```

Check `agent/memory/daily/YYYY-MM-DD.md` for plan + finance sections.

## Architecture map

```text
Telegram bot → Cursor SDK bridge → orchestrator
                                      ├── daily agent (plan → execute → log)
                                      ├── finance executor (paper default)
                                      ├── bounty scanner (draft only)
                                      └── git commit agent/memory/
```

Read `agent/instructions.md` for the autonomy matrix and approval gates.

## Finance safety

- **Paper mode by default** — trades logged in SQLite, not executed
- Live trades require `FINANCE_LIVE=true` **and** Telegram approval
- Risk engine caps trade size; geoblock checks on Polymarket
- Start with 7 days paper before any live capital

## Customization

| Area | Path |
|------|------|
| Daily prompt | `agent/tasks/daily_prompt.md` |
| Income lanes | `agent/memory/income_plan.md` |
| Site content | `site/content/` |
| Skills | `agent/skills/*/SKILL.md` |

## Updates (6 months included)

- Changelog in repo root
- Pull latest: `git pull && ./scripts/deploy-from-git.sh`
- Breaking changes announced in Gumroad email

## Support

- Email: [your support email]
- Telegram community: [optional link]
- No SLA on intro price ($19 launch)

## License

Personal / single-server use. No resale of the template as-is. Commercial use on your own infrastructure OK.

---

*Built from a live stack at [mpeshekhonov.ru](https://mpeshekhonov.ru) — see blog post «Self-hosted agent stack».*
