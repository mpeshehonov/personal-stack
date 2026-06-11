# Git-based deployment

Replace full-tree `rsync` with Git pull on the server. Docker builds the Next.js site on the server; secrets and runtime state never enter the repo.

## What stays out of Git

| Path | Reason |
|------|--------|
| `secrets/` (except `*.template` and `.env.example`) | API keys, bot tokens |
| `site/node_modules/`, `site/.next/` | Built on server inside Docker |
| `.venv/` | Python venv on server |
| `agent/state.sqlite` | Runtime orchestrator state |
| `vpn/**/certs/`, live VPN configs (`config-*.yaml`, `config.json`, `WORKING.txt`, subscription URLs) | Passwords, Reality keys, TLS certs |

Initial repo size (tracked files only): **~540 KB**. A typical `rsync` of the same tree (with excludes) is **~500 KB every deploy**; after bootstrap, `git pull` transfers only diffs (often **5–50 KB**).

---

## 1. Create GitHub repo (local)

```bash
cd /Users/m.peshekhonov/Projects/personal-stack

# Verify nothing sensitive is staged
git status
git check-ignore -v secrets/.env.cursor vpn/hysteria2/certs/cert.pem agent/state.sqlite

# Initial commit (if not done yet)
git add -A
git status   # confirm no secrets/, no .pem, no state.sqlite
git commit -m "chore: initial commit for git-based deploy"
```

On GitHub: create a **private** repository named `personal-stack` (no README/license — empty repo).

```bash
git remote add origin git@github.com:YOUR_USER/personal-stack.git
git push -u origin main
```

Use a private repo. Do not commit real `.env` files or VPN certificates.

---

## 2. Server SSH access to GitHub (one-time)

SSH to the server works as `agent@89.124.70.216`.

### Option A — Deploy key (recommended)

On the server as `agent`:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/github_personal_stack -N "" -C "personal-stack-deploy"
cat ~/.ssh/github_personal_stack.pub
```

In GitHub → repo **Settings → Deploy keys → Add deploy key**:

- Title: `personal-stack-server`
- Key: paste public key
- **Allow write access**: off (read-only)

```bash
cat >> ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_personal_stack
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config

ssh -T git@github.com   # expect: "Hi USER/personal-stack! ..."
```

### Option B — Personal SSH key

If `agent` already has GitHub SSH access, skip the deploy key and use `git@github.com:YOUR_USER/personal-stack.git` directly.

---

## 3. Bootstrap server checkout (one-time)

**Push from local first** (step 1), then on the server:

```bash
ssh agent@89.124.70.216

GITHUB_REPO=git@github.com:YOUR_USER/personal-stack.git \
  /opt/personal-stack/scripts/bootstrap-git-on-server.sh
```

This script:

1. Backs up `secrets/`, `.venv/`, `agent/state.sqlite`, VPN certs
2. Clones (or attaches `origin` and resets to `main`)
3. Restores server-only paths and fixes permissions

Then run a full deploy:

```bash
cd /opt/personal-stack
./scripts/deploy-from-git.sh
```

### Manual alternative (fresh clone)

```bash
sudo -u agent bash -c '
  BACKUP=/tmp/ps-backup-$$
  mkdir -p $BACKUP
  cp -a /opt/personal-stack/secrets $BACKUP/ 2>/dev/null || true
  cp -a /opt/personal-stack/.venv $BACKUP/ 2>/dev/null || true
  cp -a /opt/personal-stack/agent/state.sqlite $BACKUP/ 2>/dev/null || true
  rm -rf /opt/personal-stack
  git clone git@github.com:YOUR_USER/personal-stack.git /opt/personal-stack
  cp -a $BACKUP/secrets /opt/personal-stack/ 2>/dev/null || true
  cp -a $BACKUP/.venv /opt/personal-stack/ 2>/dev/null || true
  cp -a $BACKUP/state.sqlite /opt/personal-stack/agent/ 2>/dev/null || true
  chmod 700 /opt/personal-stack/secrets
  rm -rf $BACKUP
'
```

---

## 4. Day-to-day deploy

### From your machine

```bash
./scripts/deploy-local.sh
```

This runs `git push origin main`, then:

```bash
ssh agent@89.124.70.216 'cd /opt/personal-stack && ./scripts/deploy-from-git.sh'
```

Remote-only (code already pushed):

```bash
SKIP_PUSH=1 ./scripts/deploy-local.sh
```

### On the server

```bash
cd /opt/personal-stack && ./scripts/deploy-from-git.sh
```

`deploy-from-git.sh` will:

1. `git pull --ff-only`
2. Fix ownership (`agent:agent`) and `secrets/` permissions
3. `pip install` into `.venv`
4. `docker compose build site && docker compose up -d site caddy` (never full `up -d` — avoids touching redis and limits Caddy churn)
5. Restart `agent-orchestrator` and `telegram-bot`
6. Reload Caddy, run `vpn/ensure-up.sh`, and health-check `/resume`

Site deploy does **not** restart VPN containers. See [VPN.md](VPN.md).

Environment overrides:

```bash
RELOAD_CADDY=0 RESTART_SYSTEMD=0 ./scripts/deploy-from-git.sh   # site-only
GIT_BRANCH=main STACK_DIR=/opt/personal-stack ./scripts/deploy-from-git.sh
```

---

## 5. Optional — GitHub Actions auto-deploy

Workflow: `.github/workflows/deploy.yml` (disabled until secrets are set).

In GitHub → **Settings → Secrets and variables → Actions**, add:

| Secret | Example |
|--------|---------|
| `DEPLOY_HOST` | `89.124.70.216` |
| `DEPLOY_USER` | `agent` |
| `DEPLOY_KEY` | Private SSH key with access to `agent@` server |
| `DEPLOY_PATH` | `/opt/personal-stack` (optional) |

Push to `main` then runs the same `deploy-from-git.sh` on the server. You can also trigger manually via **Actions → Deploy → Run workflow**.

---

## Transfer size comparison

| Method | First deploy | Typical update |
|--------|--------------|----------------|
| `rsync` (exclude node_modules, .next, .venv, secrets) | ~500 KB | ~500 KB (full tree scan) |
| `git clone` | ~540 KB pack | — |
| `git pull` | — | ~5–50 KB (changed files only) |

Docker still downloads base images and npm packages on the server during `docker compose build site`; that is unchanged and avoids shipping `.next/` or `node_modules/` over SSH.

---

## Troubleshooting

**`git pull` would overwrite untracked files**  
Run `./scripts/bootstrap-git-on-server.sh` once, or move conflicting files aside.

**Permission denied on `.git` or docker**  
Ensure `agent` is in the `docker` group: `groups agent` should include `docker`. Re-login after `usermod -aG docker agent`.

**Site build fails**  
Check `docker compose build site` logs. Source is built inside the container; host `site/.next` is not used.

**Secrets missing after clone**  
Restore from backup or copy templates:

```bash
cp secrets/.env.example secrets/.env.cursor   # fill keys
cp secrets/.env.telegram.template secrets/.env.telegram
chmod 600 secrets/.env.*
```
