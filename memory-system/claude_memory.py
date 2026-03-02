#!/usr/bin/env python3
"""
Claude Memory System — SQLite-backed persistent memory with FTS5 full-text
search and trigram fuzzy matching.

Usage:
    claude-memory add "Title" "Content" --tags tag1,tag2 --category gotchas
    claude-memory search "fuzzy query here"
    claude-memory fuzzy "apii kee"  # typo-tolerant search
    claude-memory list --category gotchas --limit 10
    claude-memory get <id>
    claude-memory update <id> --content "new content" --tags new,tags
    claude-memory delete <id>
    claude-memory export --format md|json|claude
    claude-memory import <file.json>
    claude-memory stats
    claude-memory related <id>  # find related memories

Store at: ~/.claude/memory/claude_memory.db
"""

import sqlite3
import json
import sys
import os
import argparse
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_DB_PATH = Path.home() / ".claude" / "memory" / "claude_memory.db"

CATEGORIES = [
    "commands",      # Build/test/dev commands
    "architecture",  # Project structure and patterns
    "gotchas",       # Non-obvious things that waste time
    "config",        # Environment, config quirks
    "workflow",      # How to do things
    "patterns",      # Code patterns and conventions
    "debug",         # Debugging knowledge
    "api",           # API endpoints, contracts, keys info
    "dependencies",  # Package relationships
    "general",       # Catch-all
]

# ── Database ──────────────────────────────────────────────────────────────────

def get_db(db_path=None):
    """Get a database connection, creating schema if needed."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Core memories table
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            project TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            source TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
        CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);
        CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
    """)

    # FTS5 full-text search index
    # tokenize='porter unicode61' gives us stemming (e.g., "running" matches "run")
    # and unicode support
    conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            title,
            content,
            tags,
            category,
            content='memories',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        -- Triggers to keep FTS index in sync
        CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memories_fts(rowid, title, content, tags, category)
            VALUES (new.id, new.title, new.content, new.tags, new.category);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, category)
            VALUES ('delete', old.id, old.title, old.content, old.tags, old.category);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, title, content, tags, category)
            VALUES ('delete', old.id, old.title, old.content, old.tags, old.category);
            INSERT INTO memories_fts(rowid, title, content, tags, category)
            VALUES (new.id, new.title, new.content, new.tags, new.category);
        END;
    """)

    return conn


# ── Trigram Fuzzy Matching ────────────────────────────────────────────────────

def trigrams(s):
    """Generate trigrams from a string for fuzzy matching."""
    s = s.lower().strip()
    # Pad with spaces for edge trigrams
    s = f"  {s} "
    return [s[i:i+3] for i in range(len(s) - 2)]


def trigram_similarity(a, b):
    """Calculate trigram similarity between two strings (0.0 to 1.0)."""
    if not a or not b:
        return 0.0
    tg_a = set(trigrams(a))
    tg_b = set(trigrams(b))
    if not tg_a or not tg_b:
        return 0.0
    intersection = tg_a & tg_b
    union = tg_a | tg_b
    return len(intersection) / len(union)


# ── CRUD Operations ──────────────────────────────────────────────────────────

def add_memory(conn, title, content, category="general", project="",
               tags="", source=""):
    """Add a new memory."""
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("""
        INSERT INTO memories (title, content, category, project, tags, source,
                             created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, content, category, project, tags, source, now, now))
    conn.commit()
    return cur.lastrowid


def get_memory(conn, memory_id):
    """Get a single memory by ID."""
    row = conn.execute("SELECT * FROM memories WHERE id = ?",
                       (memory_id,)).fetchone()
    if row:
        # Bump access count
        conn.execute("""
            UPDATE memories SET access_count = access_count + 1,
                               last_accessed = ?
            WHERE id = ?
        """, (datetime.now(timezone.utc).isoformat(), memory_id))
        conn.commit()
    return row


def update_memory(conn, memory_id, **kwargs):
    """Update a memory's fields."""
    allowed = {"title", "content", "category", "project", "tags", "source"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return False

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [memory_id]

    conn.execute(f"UPDATE memories SET {set_clause} WHERE id = ?", values)
    conn.commit()
    return True


def delete_memory(conn, memory_id):
    """Delete a memory."""
    conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()


def list_memories(conn, category=None, project=None, tag=None, limit=20,
                  offset=0):
    """List memories with optional filters."""
    query = "SELECT * FROM memories WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if project:
        query += " AND project = ?"
        params.append(project)
    if tag:
        query += " AND (',' || tags || ',') LIKE ?"
        params.append(f"%,{tag},%")

    query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    return conn.execute(query, params).fetchall()


# ── Search ───────────────────────────────────────────────────────────────────

def fts_search(conn, query, limit=20):
    """Full-text search using FTS5 with BM25 ranking.

    Supports:
      - Simple terms: "python testing"
      - Phrases: '"api key"'
      - Prefix: "config*"
      - Boolean: "python AND NOT django"
      - Column filter: "title:setup"
    """
    rows = conn.execute("""
        SELECT m.*, rank
        FROM memories_fts fts
        JOIN memories m ON m.id = fts.rowid
        WHERE memories_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit)).fetchall()
    return rows


def fuzzy_search(conn, query, threshold=0.15, limit=20):
    """Fuzzy search using trigram similarity for typo tolerance.

    Lower threshold = more results (looser matching).
    """
    # Get all memories (for small-medium DBs this is fine;
    # for large DBs we'd use a trigram index table)
    all_memories = conn.execute(
        "SELECT * FROM memories ORDER BY updated_at DESC"
    ).fetchall()

    scored = []
    for mem in all_memories:
        # Score against title, content, and tags
        title_score = trigram_similarity(query, mem["title"]) * 2.0  # Boost title
        content_score = trigram_similarity(query, mem["content"])
        tag_score = trigram_similarity(query, mem["tags"]) * 1.5  # Boost tags
        best = max(title_score, content_score, tag_score)

        if best >= threshold:
            scored.append((best, mem))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]


def smart_search(conn, query, limit=20):
    """Combined search: tries FTS5 first, falls back to fuzzy if few results."""
    # Try FTS5 first
    try:
        fts_results = fts_search(conn, query, limit)
    except sqlite3.OperationalError:
        # FTS query syntax error — fall through to fuzzy
        fts_results = []

    if len(fts_results) >= 3:
        return [("fts", r) for r in fts_results]

    # Supplement with fuzzy results
    fuzzy_results = fuzzy_search(conn, query, limit=limit)

    # Merge, dedup by ID
    seen_ids = {r["id"] for r in fts_results}
    combined = [("fts", r) for r in fts_results]

    for score, mem in fuzzy_results:
        if mem["id"] not in seen_ids:
            combined.append(("fuzzy", mem))
            seen_ids.add(mem["id"])

    return combined[:limit]


def find_related(conn, memory_id, limit=5):
    """Find memories related to a given memory using content similarity."""
    mem = get_memory(conn, memory_id)
    if not mem:
        return []

    # Use the memory's title + tags as search terms
    search_text = f"{mem['title']} {mem['tags']}"
    results = fuzzy_search(conn, search_text, threshold=0.1, limit=limit + 1)

    # Exclude the source memory itself
    return [(score, m) for score, m in results if m["id"] != memory_id][:limit]


# ── Export / Import ──────────────────────────────────────────────────────────

def export_memories(conn, fmt="json", category=None, project=None):
    """Export memories in various formats."""
    memories = list_memories(conn, category=category, project=project,
                            limit=10000)

    if fmt == "json":
        data = [dict(m) for m in memories]
        return json.dumps(data, indent=2, default=str)

    elif fmt == "md":
        lines = ["# Claude Memory Export\n"]
        lines.append(f"*Exported: {datetime.now(timezone.utc).isoformat()}*\n")

        current_cat = None
        for m in sorted(memories, key=lambda x: x["category"]):
            if m["category"] != current_cat:
                current_cat = m["category"]
                lines.append(f"\n## {current_cat.title()}\n")

            lines.append(f"### {m['title']}")
            if m["tags"]:
                lines.append(f"*Tags: {m['tags']}*")
            if m["project"]:
                lines.append(f"*Project: {m['project']}*")
            lines.append(f"\n{m['content']}\n")

        return "\n".join(lines)

    elif fmt == "claude":
        # Export as a CLAUDE.md-compatible format — dense, token-efficient
        lines = ["# Memory Context\n"]

        by_cat = {}
        for m in memories:
            by_cat.setdefault(m["category"], []).append(m)

        for cat in sorted(by_cat):
            lines.append(f"## {cat.title()}\n")
            for m in by_cat[cat]:
                tag_str = f" [{m['tags']}]" if m["tags"] else ""
                lines.append(f"- **{m['title']}**{tag_str}: {m['content']}")
            lines.append("")

        return "\n".join(lines)

    else:
        raise ValueError(f"Unknown format: {fmt}")


def import_memories(conn, filepath):
    """Import memories from a JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    count = 0
    for m in data:
        add_memory(
            conn,
            title=m.get("title", "Untitled"),
            content=m.get("content", ""),
            category=m.get("category", "general"),
            project=m.get("project", ""),
            tags=m.get("tags", ""),
            source=m.get("source", f"import:{filepath}"),
        )
        count += 1

    return count


# ── Stats ────────────────────────────────────────────────────────────────────

def get_stats(conn):
    """Get memory database statistics."""
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    cats = conn.execute("""
        SELECT category, COUNT(*) as cnt FROM memories
        GROUP BY category ORDER BY cnt DESC
    """).fetchall()
    projects = conn.execute("""
        SELECT project, COUNT(*) as cnt FROM memories
        WHERE project != ''
        GROUP BY project ORDER BY cnt DESC
    """).fetchall()
    most_accessed = conn.execute("""
        SELECT id, title, access_count FROM memories
        ORDER BY access_count DESC LIMIT 5
    """).fetchall()
    recent = conn.execute("""
        SELECT id, title, updated_at FROM memories
        ORDER BY updated_at DESC LIMIT 5
    """).fetchall()

    # Tag frequency
    all_tags = []
    for row in conn.execute("SELECT tags FROM memories WHERE tags != ''"):
        all_tags.extend(t.strip() for t in row[0].split(",") if t.strip())
    tag_freq = Counter(all_tags).most_common(10)

    return {
        "total": total,
        "by_category": [(dict(r)["category"], dict(r)["cnt"]) for r in cats],
        "by_project": [(dict(r)["project"], dict(r)["cnt"]) for r in projects],
        "most_accessed": [dict(r) for r in most_accessed],
        "recent": [dict(r) for r in recent],
        "top_tags": tag_freq,
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def format_memory(mem, verbose=False):
    """Format a memory for display."""
    lines = []
    lines.append(f"  [{mem['id']}] {mem['title']}")

    meta = []
    if mem["category"]:
        meta.append(f"cat:{mem['category']}")
    if mem["tags"]:
        meta.append(f"tags:{mem['tags']}")
    if mem["project"]:
        meta.append(f"proj:{mem['project']}")
    if meta:
        lines.append(f"       {' | '.join(meta)}")

    if verbose:
        content = mem["content"]
        if len(content) > 200:
            content = content[:200] + "..."
        for line in content.split("\n"):
            lines.append(f"       {line}")
        lines.append(f"       accessed:{mem['access_count']}x | "
                     f"updated:{mem['updated_at'][:10]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Claude Memory System — persistent, searchable knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              %(prog)s add "pytest gotcha" "Tests must run with --runInBand" -c gotchas -t testing,pytest
              %(prog)s search "pytest"
              %(prog)s fuzzy "pytst"           # typo-tolerant
              %(prog)s smart "api key setup"    # FTS5 + fuzzy combined
              %(prog)s list -c gotchas
              %(prog)s export --format claude   # CLAUDE.md-compatible output
              %(prog)s related 42               # memories related to #42
              %(prog)s stats
        """),
    )
    parser.add_argument("--db", default=None, help="Database path")

    sub = parser.add_subparsers(dest="command", help="Command")

    # add
    p_add = sub.add_parser("add", help="Add a new memory")
    p_add.add_argument("title", help="Memory title")
    p_add.add_argument("content", help="Memory content")
    p_add.add_argument("-c", "--category", default="general",
                       choices=CATEGORIES)
    p_add.add_argument("-p", "--project", default="")
    p_add.add_argument("-t", "--tags", default="")
    p_add.add_argument("-s", "--source", default="cli")

    # search (FTS5)
    p_search = sub.add_parser("search", help="Full-text search (FTS5)")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-n", "--limit", type=int, default=20)

    # fuzzy
    p_fuzzy = sub.add_parser("fuzzy", help="Fuzzy/typo-tolerant search")
    p_fuzzy.add_argument("query", help="Fuzzy search query")
    p_fuzzy.add_argument("-n", "--limit", type=int, default=20)
    p_fuzzy.add_argument("--threshold", type=float, default=0.15)

    # smart (combined)
    p_smart = sub.add_parser("smart", help="Smart search (FTS5 + fuzzy)")
    p_smart.add_argument("query", help="Search query")
    p_smart.add_argument("-n", "--limit", type=int, default=20)

    # list
    p_list = sub.add_parser("list", help="List memories")
    p_list.add_argument("-c", "--category", default=None)
    p_list.add_argument("-p", "--project", default=None)
    p_list.add_argument("-t", "--tag", default=None)
    p_list.add_argument("-n", "--limit", type=int, default=20)
    p_list.add_argument("-v", "--verbose", action="store_true")

    # get
    p_get = sub.add_parser("get", help="Get a memory by ID")
    p_get.add_argument("id", type=int)

    # update
    p_update = sub.add_parser("update", help="Update a memory")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--title", default=None)
    p_update.add_argument("--content", default=None)
    p_update.add_argument("-c", "--category", default=None)
    p_update.add_argument("-p", "--project", default=None)
    p_update.add_argument("-t", "--tags", default=None)

    # delete
    p_del = sub.add_parser("delete", help="Delete a memory")
    p_del.add_argument("id", type=int)

    # export
    p_export = sub.add_parser("export", help="Export memories")
    p_export.add_argument("-f", "--format", default="json",
                          choices=["json", "md", "claude"])
    p_export.add_argument("-c", "--category", default=None)
    p_export.add_argument("-p", "--project", default=None)
    p_export.add_argument("-o", "--output", default=None,
                          help="Output file (default: stdout)")

    # import
    p_import = sub.add_parser("import", help="Import memories from JSON")
    p_import.add_argument("file", help="JSON file to import")

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # related
    p_related = sub.add_parser("related", help="Find related memories")
    p_related.add_argument("id", type=int)
    p_related.add_argument("-n", "--limit", type=int, default=5)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    conn = get_db(args.db)

    try:
        if args.command == "add":
            mid = add_memory(conn, args.title, args.content, args.category,
                            args.project, args.tags, args.source)
            print(f"✓ Added memory #{mid}: {args.title}")

        elif args.command == "search":
            results = fts_search(conn, args.query, args.limit)
            if not results:
                print(f"No results for: {args.query}")
                print("Tip: try 'fuzzy' or 'smart' for typo-tolerant search")
            else:
                print(f"── FTS5 results for: {args.query} ({len(results)} found) ──\n")
                for r in results:
                    print(format_memory(r, verbose=True))
                    print()

        elif args.command == "fuzzy":
            results = fuzzy_search(conn, args.query, args.threshold, args.limit)
            if not results:
                print(f"No fuzzy matches for: {args.query}")
            else:
                print(f"── Fuzzy results for: {args.query} ({len(results)} found) ──\n")
                for score, mem in results:
                    print(f"  ({score:.0%}) {format_memory(mem, verbose=True)}")
                    print()

        elif args.command == "smart":
            results = smart_search(conn, args.query, args.limit)
            if not results:
                print(f"No results for: {args.query}")
            else:
                print(f"── Smart search: {args.query} ({len(results)} found) ──\n")
                for method, mem in results:
                    tag = "●" if method == "fts" else "○"
                    print(f"  {tag} {format_memory(mem, verbose=True)}")
                    print()
                print("● = exact match  ○ = fuzzy match")

        elif args.command == "list":
            results = list_memories(conn, args.category, args.project,
                                   args.tag, args.limit)
            if not results:
                print("No memories found.")
            else:
                print(f"── Memories ({len(results)}) ──\n")
                for m in results:
                    print(format_memory(m, verbose=getattr(args, 'verbose', False)))
                    print()

        elif args.command == "get":
            mem = get_memory(conn, args.id)
            if not mem:
                print(f"Memory #{args.id} not found.")
                sys.exit(1)
            print(f"── Memory #{mem['id']} ──\n")
            print(f"  Title:    {mem['title']}")
            print(f"  Category: {mem['category']}")
            print(f"  Project:  {mem['project'] or '(none)'}")
            print(f"  Tags:     {mem['tags'] or '(none)'}")
            print(f"  Source:   {mem['source'] or '(none)'}")
            print(f"  Created:  {mem['created_at']}")
            print(f"  Updated:  {mem['updated_at']}")
            print(f"  Accessed: {mem['access_count']}x")
            print(f"\n  Content:\n")
            for line in mem["content"].split("\n"):
                print(f"    {line}")

        elif args.command == "update":
            ok = update_memory(conn, args.id, title=args.title,
                              content=args.content, category=args.category,
                              project=args.project, tags=args.tags)
            if ok:
                print(f"✓ Updated memory #{args.id}")
            else:
                print("Nothing to update.")

        elif args.command == "delete":
            delete_memory(conn, args.id)
            print(f"✓ Deleted memory #{args.id}")

        elif args.command == "export":
            output = export_memories(conn, args.format, args.category,
                                    args.project)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
                print(f"✓ Exported to {args.output}")
            else:
                print(output)

        elif args.command == "import":
            count = import_memories(conn, args.file)
            print(f"✓ Imported {count} memories from {args.file}")

        elif args.command == "stats":
            s = get_stats(conn)
            print(f"── Memory Stats ──\n")
            print(f"  Total memories: {s['total']}\n")

            if s["by_category"]:
                print("  By category:")
                for cat, cnt in s["by_category"]:
                    bar = "█" * min(cnt, 30)
                    print(f"    {cat:15s} {cnt:4d} {bar}")

            if s["by_project"]:
                print("\n  By project:")
                for proj, cnt in s["by_project"]:
                    print(f"    {proj:20s} {cnt}")

            if s["top_tags"]:
                print("\n  Top tags:")
                for tag, cnt in s["top_tags"]:
                    print(f"    {tag:15s} {cnt}")

            if s["most_accessed"]:
                print("\n  Most accessed:")
                for m in s["most_accessed"]:
                    if m["access_count"] > 0:
                        print(f"    [{m['id']}] {m['title']} ({m['access_count']}x)")

            if s["recent"]:
                print("\n  Recently updated:")
                for m in s["recent"]:
                    print(f"    [{m['id']}] {m['title']} ({m['updated_at'][:10]})")

        elif args.command == "related":
            results = find_related(conn, args.id, args.limit)
            if not results:
                print(f"No related memories found for #{args.id}")
            else:
                mem = conn.execute("SELECT title FROM memories WHERE id = ?",
                                  (args.id,)).fetchone()
                print(f"── Related to #{args.id}: {mem['title']} ──\n")
                for score, m in results:
                    print(f"  ({score:.0%}) {format_memory(m)}")
                    print()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
