# Cross-Project Templates Guide

Reusable configs and templates for new projects. Copy what you need.

## Quick Setup for a New Project

```bash
# 1. One-time global setup (do this once ever)
mkdir -p ~/.claude ~/.env.shared
cp templates/global-CLAUDE.md.template ~/.claude/CLAUDE.md
cp templates/env.master.template ~/.env.shared/.env.master
chmod 700 ~/.env.shared && chmod 600 ~/.env.shared/.env.master
# Edit both files with your actual values

# 2. Per-project setup (do this per repo)
cp templates/CLAUDE.md.template ./CLAUDE.md
cp templates/.editorconfig ./.editorconfig
cp templates/.gitignore.template ./.gitignore
cp -r templates/.github ./.github
cp templates/CLAUDE.local.md.template ./.claude.local.md
cp templates/envrc.template ./.envrc  # If using direnv

# 3. Fill in the placeholders
```

## What's Included

### CLAUDE.md Templates

| Template | When to Use |
|----------|-------------|
| `CLAUDE.md.template` | Standard single-project repo |
| `CLAUDE.monorepo.md.template` | Monorepo with multiple packages |
| `CLAUDE.local.md.template` | Personal preferences (gitignored) |
| `global-CLAUDE.md.template` | Global user defaults at `~/.claude/CLAUDE.md` |

### Memory & API Keys

| Guide | Purpose |
|-------|---------|
| `MEMORY-GUIDE.md` | How the CLAUDE.md hierarchy works as persistent memory |
| `API-KEYS-GUIDE.md` | Secure central API key management across projects |

### Environment Templates

| File | Purpose |
|------|---------|
| `env.master.template` | Master API key vault at `~/.env.shared/.env.master` |
| `envrc.template` | `direnv` config that sources master keys + project overrides |

### GitHub Configs

| File | Purpose |
|------|---------|
| `.github/dependabot.yml` | Auto-update dependencies weekly, grouped by type |
| `.github/PULL_REQUEST_TEMPLATE.md` | Standardized PR descriptions |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug reports |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature requests |
| `.github/workflows/ci.yml` | Lint → Test → Build pipeline (Node.js, adjust as needed) |

### Editor / Git Configs

| File | Purpose |
|------|---------|
| `.editorconfig` | Consistent indentation/encoding across editors |
| `.gitignore.template` | Comprehensive ignore for Node/Python/IDE/OS |

## CLAUDE.md Best Practices

These principles come from the `claude-md-improver` skill's quality rubric:

**Token budget is real** — every line in CLAUDE.md consumes context window. Optimise for density.

**What earns its place:**
- Copy-paste-ready commands
- Architecture maps showing where things live
- Gotchas that prevent repeat debugging
- Non-obvious patterns ("why we do it this way")

**What wastes tokens:**
- Generic advice ("use meaningful variable names")
- Verbose explanations of things the code already shows
- One-off bug descriptions
- Restating README content

**Quality scoring** (100-point rubric):
- Commands/workflows: 20 pts
- Architecture clarity: 20 pts
- Non-obvious patterns: 15 pts
- Conciseness: 15 pts
- Currency (up-to-date): 15 pts
- Actionability: 15 pts

**File hierarchy** (Claude auto-discovers all of these):
- `~/.claude/CLAUDE.md` — Global user defaults
- `./CLAUDE.md` — Project root (shared via git)
- `./.claude.local.md` — Personal overrides (gitignored)
- `./packages/*/CLAUDE.md` — Package-specific in monorepos

## GitHub Repo Settings Worth Enabling

These aren't files but settings you should toggle in the GitHub UI for every repo:

**Under Settings → General:**
- Enable "Automatically delete head branches" after merge
- Set default branch to `main`
- Enable "Always suggest updating pull request branches"

**Under Settings → Branches:**
- Add branch protection rule for `main`:
  - Require pull request before merging
  - Require status checks to pass (link to your CI workflow)
  - Require branches to be up to date before merging

**Under Settings → Actions → General:**
- Set "Fork pull request workflows" to "Require approval for first-time contributors"

**Under Settings → Code security:**
- Enable Dependabot alerts
- Enable Dependabot security updates
- Enable secret scanning
