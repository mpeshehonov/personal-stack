# Personal Stack — Autonomous Agent Server

Self-hosted stack: Next.js resume site, Python orchestrator, Cursor SDK agent, Telegram bot, finance module with risk engine, bug bounty scanner.

## Server layout

```
/opt/personal-stack/
├── docker-compose.yml
├── site/                 # Next.js
├── agent/                # Python services
├── secrets/              # API keys (not in git)
└── scripts/
```

## Quick deploy

**Git-based deploy (recommended):** see [docs/DEPLOY.md](docs/DEPLOY.md).

```bash
# One-time: push repo to GitHub, bootstrap server with deploy key
# Day-to-day from your machine:
./scripts/deploy-local.sh

# Or on server:
ssh agent@89.124.70.216 'cd /opt/personal-stack && ./scripts/deploy-from-git.sh'
```

First-time server setup:

```bash
# On fresh Ubuntu as root:
bash scripts/bootstrap-server.sh

# On server as agent — configure secrets, then full stack install:
cd /opt/personal-stack
cp secrets/.env.example secrets/.env.cursor   # fill in keys
cp secrets/.env.telegram.template secrets/.env.telegram
cp secrets/.env.finance.template secrets/.env.finance
bash scripts/deploy-stack.sh
```

## Secrets

| File | Keys |
|------|------|
| `secrets/.env.cursor` | `CURSOR_API_KEY` |
| `secrets/.env.telegram` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS` |
| `secrets/.env.finance` | `FINANCE_LIVE`, `MAX_TRADE_USD`, `YOUR_WALLET_ADDRESS`, ... |

## Telegram commands

- `/status` — health + last run
- `/task <text>` — queue agent task
- `/ask <text>` — one-shot Cursor prompt
- `/pause` / `/resume` — autonomy control
- `/bounty` — pending submit-ready reports
- `/bounty hunt` — force research now
- `/approve bounty <id>` — approve and auto-submit (HackerOne)

## Local dev

```bash
cd site && npm install && npm run dev
cd agent && python3 -m venv .venv && pip install -r requirements.txt
PYTHONPATH=agent python -m orchestrator.main
```
