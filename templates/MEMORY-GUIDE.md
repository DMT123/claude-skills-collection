# Claude Memory & Shared Context Guide

How to set up persistent memory across projects and sessions.

## The Memory Hierarchy

Claude auto-discovers CLAUDE.md files in a cascade. Put shared things at the top, project-specific things at the bottom:

```
~/.claude/CLAUDE.md              ← Global (all projects, all sessions)
  └── ./CLAUDE.md                ← Project root (shared with team via git)
       └── ./.claude.local.md   ← Personal overrides (gitignored)
            └── ./packages/*/CLAUDE.md  ← Package-specific (monorepos)
```

Everything higher in the chain is automatically included in every session below it. This means:
- Your coding preferences go in `~/.claude/CLAUDE.md` (written once, applies everywhere)
- Project commands/architecture go in `./CLAUDE.md` (per-repo, committed)
- Your local env quirks go in `./.claude.local.md` (per-repo, gitignored)

## Setup

### 1. Global Memory (do this once)

```bash
mkdir -p ~/.claude
cp templates/global-CLAUDE.md.template ~/.claude/CLAUDE.md
# Edit with your actual preferences
```

This is the single most impactful thing you can do — it stops you repeating yourself in every project.

### 2. Per-Project Memory (do this per repo)

```bash
cp templates/CLAUDE.md.template ./CLAUDE.md
cp templates/CLAUDE.local.md.template ./.claude.local.md
echo ".claude.local.md" >> .gitignore
```

### 3. Monorepo Packages (optional)

```bash
# In each significant package:
cat > packages/api/CLAUDE.md << 'EOF'
# API Package
Express REST API with Prisma ORM.
## Commands
| Command | Purpose |
|---------|---------|
| `npm run dev` | Dev server on :3001 |
| `npm run db:migrate` | Run Prisma migrations |
## Gotchas
- Must run migrations before first dev server start
EOF
```

## What Goes Where

| Content | Location | Why |
|---------|----------|-----|
| Coding style preferences | `~/.claude/CLAUDE.md` | Same across all projects |
| Git workflow preferences | `~/.claude/CLAUDE.md` | Same across all projects |
| Commit message format | `~/.claude/CLAUDE.md` | Same across all projects |
| Tool preferences (pnpm, etc.) | `~/.claude/CLAUDE.md` | Same across all projects |
| Build/test/dev commands | `./CLAUDE.md` | Different per project |
| Architecture map | `./CLAUDE.md` | Different per project |
| Project gotchas | `./CLAUDE.md` | Different per project |
| Local DB port, paths | `./.claude.local.md` | Different per machine |
| API key locations | `./.claude.local.md` | Never committed |

## Updating Memory

Two approaches:

**Manual:** Edit the relevant CLAUDE.md file directly when you learn something new about a project.

**Auto via `#` shortcut:** During a Claude Code session, press `#` to have Claude automatically suggest additions to CLAUDE.md based on what was learned in the session.

**Via skill:** Use the `claude-md-improver` skill to audit and improve existing CLAUDE.md files: ask Claude to "audit my CLAUDE.md files".

## Avoiding Duplication

The most common mistake is duplicating global preferences in every project's CLAUDE.md. Before adding something to a project CLAUDE.md, ask: "Is this specific to THIS project, or is it just how I always work?"

If it's how you always work → put it in `~/.claude/CLAUDE.md`
If it's project-specific → put it in `./CLAUDE.md`
If it's machine-specific → put it in `./.claude.local.md`
