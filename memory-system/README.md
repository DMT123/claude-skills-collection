# Claude Memory System

SQLite-backed persistent memory with full-text search (FTS5) and fuzzy matching for Claude Code / development workflows.

## Why?

CLAUDE.md files are great for per-project context, but knowledge gets lost between projects. This system gives you a searchable knowledge base that spans all your work — gotchas, patterns, commands, architecture decisions — with typo-tolerant fuzzy search.

## Quick Start

```bash
# Add your first memory
python3 claude_memory.py add "Prisma gotcha" \
  "Always run prisma generate after migrate dev" \
  -c gotchas -t prisma,database -p my-project

# Search (exact)
python3 claude_memory.py search "prisma"

# Search (typo-tolerant)
python3 claude_memory.py fuzzy "prizma migrat"

# Smart search (FTS5 first, fuzzy fallback)
python3 claude_memory.py smart "database migration"
```

## Features

| Feature | How |
|---------|-----|
| Full-text search | FTS5 with BM25 ranking + porter stemming |
| Fuzzy search | Trigram similarity (Jaccard coefficient) |
| Smart search | FTS5 → fuzzy cascade for best of both |
| Categories | commands, architecture, gotchas, config, workflow, patterns, debug, api, dependencies, general |
| Tags | Comma-separated, searchable and filterable |
| Projects | Associate memories with specific repos |
| Export | JSON, Markdown, or CLAUDE.md-compatible format |
| Import | Roundtrip via JSON |
| Related | Find similar memories by content similarity |
| Stats | Category/project/tag distribution, most accessed |
| Access tracking | Automatic hit counting on reads |

## Search Modes

**FTS5** — Best for known terms. Supports phrases (`"api key"`), prefixes (`docker*`), boolean (`python NOT django`), and column filters (`title:setup`).

**Fuzzy** — Best for typos and approximate recall. Uses trigram similarity — "pytst" finds "pytest", "prizma" finds "Prisma".

**Smart** — Tries FTS5 first. If fewer than 3 results, supplements with fuzzy matches. Results marked ● (exact) or ○ (fuzzy).

## Shell Integration

Source the helper in your shell profile:

```bash
# In ~/.zshrc or ~/.bashrc
source /path/to/memory-system/shell-integration.sh
```

This gives you:

| Alias | Does |
|-------|------|
| `cm search "query"` | FTS5 search |
| `cm-fuzzy "typo"` | Fuzzy search |
| `cm-smart "query"` | Smart search |
| `cm-gotcha "title" "content"` | Quick-add gotcha for current project |
| `cm-cmd "title" "content"` | Quick-add command |
| `cm-context` | Export current project's memories |
| `cm-recall` | Show memories for current directory |
| `cm-backup` | JSON backup of all memories |

## Storage

Database: `~/.claude/memory/claude_memory.db` (auto-created)

Override with `--db /path/to/other.db` on any command.

## Export Formats

```bash
# JSON (for backup/import roundtrip)
python3 claude_memory.py export -f json -o backup.json

# Markdown (for reading)
python3 claude_memory.py export -f md

# CLAUDE.md-compatible (paste into context files)
python3 claude_memory.py export -f claude -p my-project
```

## Architecture

- **SQLite WAL mode** — concurrent reads, crash-safe writes
- **FTS5 virtual table** — kept in sync via triggers on INSERT/UPDATE/DELETE
- **Porter stemmer** — "running" matches "run", "configured" matches "configure"
- **Trigram similarity** — Jaccard coefficient on character trigram sets, no external dependencies
- **Zero dependencies** — pure Python 3 stdlib (sqlite3, argparse, json)
