# Central API Key Management

How to manage API keys across multiple projects without re-entering them every time, while keeping them secure.

## The Problem

Every new project needs a `.env` file. You end up:
- Copy-pasting keys from old projects
- Searching Slack/email for keys you've forgotten
- Accidentally committing secrets to git
- Having stale keys scattered across dozens of repos

## Solution: Central `.env` Vault + Symlinks

### The Pattern

Keep ONE master file with all your API keys, then symlink or source it from each project.

```
~/.env.shared/
├── .env.master         ← All your API keys in one place
├── .env.ai             ← AI-specific keys (OpenAI, Anthropic, HF, etc.)
├── .env.cloud          ← Cloud provider keys (AWS, GCP, Vercel, etc.)
├── .env.services       ← SaaS keys (Stripe, Sentry, PostHog, etc.)
└── .env.databases      ← Database connection strings
```

### Setup

```bash
# 1. Create the vault directory
mkdir -p ~/.env.shared
chmod 700 ~/.env.shared  # Only you can read/write

# 2. Create the master file
cat > ~/.env.shared/.env.master << 'KEYS'
# ═══════════════════════════════════════════
# MASTER API KEYS — DO NOT COMMIT ANYWHERE
# Last updated: YYYY-MM-DD
# ═══════════════════════════════════════════

# AI
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HF_TOKEN=hf_...

# Cloud
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
VERCEL_TOKEN=...

# Services
SENTRY_DSN=https://...
POSTHOG_API_KEY=phc_...
STRIPE_SECRET_KEY=sk_test_...

# Databases
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
KEYS

chmod 600 ~/.env.shared/.env.master  # Read/write only for you
```

### Using in Projects

**Option A: Source from shell profile (recommended)**

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Load shared API keys into shell environment
if [ -f ~/.env.shared/.env.master ]; then
  set -a
  source ~/.env.shared/.env.master
  set +a
fi
```

Now every terminal session has your keys available. Projects using `process.env.OPENAI_API_KEY` will just work — no `.env` file needed.

**Option B: Per-project `.env` that sources the master**

Create a `.env` in each project that imports from the vault:

```bash
# .env (gitignored)
# Project-specific overrides
PORT=3000
NODE_ENV=development

# Import shared keys (works with direnv, not all .env loaders)
# For dotenv-based apps, use Option A or C instead
```

**Option C: Symlink specific key groups**

```bash
# In your project directory:
ln -s ~/.env.shared/.env.ai .env.ai
ln -s ~/.env.shared/.env.services .env.services

# In your app, load multiple env files:
# dotenv.config({ path: ['.env', '.env.ai', '.env.services'] })
```

**Option D: Use `direnv` (best for per-project overrides)**

```bash
# Install direnv
brew install direnv  # macOS
# Add to shell: eval "$(direnv hook zsh)"

# In each project, create .envrc:
cat > .envrc << 'EOF'
source ~/.env.shared/.env.master
export PORT=3000
export NODE_ENV=development
EOF

direnv allow
```

`direnv` automatically loads/unloads env vars when you `cd` into/out of a project directory.

## For CI/CD: GitHub Secrets

Your local vault is for development. For CI/CD, use GitHub's encrypted secrets:

```bash
# Set secrets via gh CLI (one-time per repo)
gh secret set OPENAI_API_KEY --body "sk-..."
gh secret set SENTRY_DSN --body "https://..."

# Or set org-wide secrets (shared across all repos)
gh secret set OPENAI_API_KEY --org your-org --body "sk-..."
```

In workflows, reference them as `${{ secrets.OPENAI_API_KEY }}`.

**For org-wide sharing**, set secrets at the organization level:
- GitHub → Organization → Settings → Secrets and variables → Actions
- Set visibility to "All repositories" or specific repos

## For Teams: Use a Secrets Manager

If multiple people need the same keys:

| Tool | Best For | Cost |
|------|----------|------|
| **1Password CLI** (`op`) | Small teams, already using 1P | $4/user/mo |
| **Doppler** | Env var management across envs | Free tier available |
| **Infisical** | Open source, self-hostable | Free / $6/user/mo |
| **AWS Secrets Manager** | AWS-heavy teams | $0.40/secret/mo |
| **Vault (HashiCorp)** | Enterprise, complex needs | Free (self-host) |

### Example: 1Password CLI

```bash
# Login
op signin

# Reference secrets directly in .env:
OPENAI_API_KEY=op://Vault/OpenAI/api-key

# Run any command with secrets injected:
op run -- npm run dev
```

### Example: Doppler

```bash
# Setup
doppler login
doppler setup  # Select project + environment

# Run with secrets injected:
doppler run -- npm run dev

# Or export to .env:
doppler secrets download --no-file --format env > .env
```

## .env.example Template

Always include this in your repos so collaborators know what keys they need:

```bash
# .env.example — Copy to .env and fill in values
# All keys available from the team vault (ask #engineering in Slack)

# Required
OPENAI_API_KEY=sk-...            # https://platform.openai.com/api-keys
DATABASE_URL=postgresql://...    # Local: see docker-compose.yml

# Optional
SENTRY_DSN=                      # Error tracking (dev can be blank)
POSTHOG_API_KEY=                 # Analytics (dev can be blank)
```

## Security Checklist

- [ ] `~/.env.shared/` has `chmod 700` (directory) and `chmod 600` (files)
- [ ] `.env` is in every project's `.gitignore`
- [ ] `.env.local` is in every project's `.gitignore`
- [ ] No API keys in any CLAUDE.md files
- [ ] `.env.example` uses placeholder values only
- [ ] CI/CD uses GitHub Secrets or a secrets manager — never env files
- [ ] Rotate keys if they were ever committed to git (even if removed later)

## Quick Reference

| Need | Solution |
|------|----------|
| Same keys everywhere locally | Source `~/.env.shared/.env.master` in shell profile |
| Per-project overrides | `direnv` with `.envrc` that sources master + adds overrides |
| CI/CD secrets | `gh secret set` or org-level GitHub Secrets |
| Team sharing | 1Password CLI, Doppler, or Infisical |
| New project setup | Copy `.env.example`, fill from vault |
