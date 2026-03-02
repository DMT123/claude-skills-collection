#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# Claude Memory Shell Integration
# Source this in your ~/.zshrc or ~/.bashrc:
#   source /path/to/claude-skills-collection/memory-system/shell-integration.sh
# ═══════════════════════════════════════════════════════════════════════

# Path to the memory CLI — adjust if you move the file
CLAUDE_MEMORY_CLI="${CLAUDE_MEMORY_CLI:-$(dirname "${BASH_SOURCE[0]:-$0}")/claude_memory.py}"

# ── Aliases ──────────────────────────────────────────────────────────

alias cm="python3 $CLAUDE_MEMORY_CLI"
alias cm-add="python3 $CLAUDE_MEMORY_CLI add"
alias cm-search="python3 $CLAUDE_MEMORY_CLI search"
alias cm-fuzzy="python3 $CLAUDE_MEMORY_CLI fuzzy"
alias cm-smart="python3 $CLAUDE_MEMORY_CLI smart"
alias cm-list="python3 $CLAUDE_MEMORY_CLI list"
alias cm-stats="python3 $CLAUDE_MEMORY_CLI stats"

# ── Quick-add functions ──────────────────────────────────────────────

# Quick-add a gotcha for the current project
# Usage: cm-gotcha "Title" "What went wrong and how to fix it"
cm-gotcha() {
    local proj=""
    if [ -f "CLAUDE.md" ] || [ -d ".git" ]; then
        proj=$(basename "$(pwd)")
    fi
    python3 "$CLAUDE_MEMORY_CLI" add "$1" "$2" -c gotchas -p "$proj" "${@:3}"
}

# Quick-add a command
# Usage: cm-cmd "Build project" "npm run build -- --watch"
cm-cmd() {
    local proj=""
    if [ -f "CLAUDE.md" ] || [ -d ".git" ]; then
        proj=$(basename "$(pwd)")
    fi
    python3 "$CLAUDE_MEMORY_CLI" add "$1" "$2" -c commands -p "$proj" "${@:3}"
}

# Quick-add a pattern
# Usage: cm-pattern "Error handling" "Always use Result<T> instead of throwing"
cm-pattern() {
    python3 "$CLAUDE_MEMORY_CLI" add "$1" "$2" -c patterns "${@:3}"
}

# ── Context Helpers ──────────────────────────────────────────────────

# Export memories for current project as CLAUDE.md-compatible context
# Usage: cm-context [project-name]
cm-context() {
    local proj="${1:-$(basename "$(pwd)")}"
    python3 "$CLAUDE_MEMORY_CLI" export -f claude -p "$proj"
}

# Dump all memories into a file suitable for pasting into CLAUDE.md
# Usage: cm-export-claude > memories-context.md
cm-export-claude() {
    python3 "$CLAUDE_MEMORY_CLI" export -f claude
}

# ── Session Hook ─────────────────────────────────────────────────────

# Auto-search memories relevant to current directory
# Call this at shell startup or when entering a project:
#   cm-recall
cm-recall() {
    local proj=$(basename "$(pwd)")
    local results
    results=$(python3 "$CLAUDE_MEMORY_CLI" list -p "$proj" -v -n 5 2>/dev/null)
    if [ -n "$results" ] && ! echo "$results" | grep -q "No memories"; then
        echo "📝 Memories for $proj:"
        echo "$results"
    fi
}

# ── Backup ───────────────────────────────────────────────────────────

# Backup memory database
# Usage: cm-backup [output-dir]
cm-backup() {
    local dir="${1:-$HOME/.claude/memory/backups}"
    mkdir -p "$dir"
    local stamp=$(date +%Y%m%d_%H%M%S)
    python3 "$CLAUDE_MEMORY_CLI" export -f json -o "$dir/memories_$stamp.json"
    echo "✓ Backed up to $dir/memories_$stamp.json"
}
