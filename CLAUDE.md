# Claude Skills Collection

Skills reference repo — no build system, no tests.

## Structure

```
core/         # Built-in Anthropic skills (docx, pdf, pptx, xlsx, etc.)
plugins/      # Official plugin skills (superpowers, plugin-dev, sentry, etc.)
marketplace/  # Marketplace skills (customer-support)
templates/    # Reusable CLAUDE.md templates and GitHub configs
```

## Commands

| Command | Purpose |
|---------|---------|
| `find . -name "SKILL.md" \| wc -l` | Count all skills |
| `grep -rl "keyword" --include="SKILL.md"` | Search skills by content |

## Conventions

- Each skill lives in its own directory with a `SKILL.md` (YAML frontmatter + instructions)
- Some skills have `references/` subdirs with additional docs
- Plugin skills use latest version only (no duplicates)

## Gotchas

- Skill YAML frontmatter `allowed-tools` field is Cursor-specific but harmless in Claude Code — keep it
- Core skills may reference files in `/mnt/.skills/` paths — these are environment-specific
- Some skills have large reference files (e.g., pptx has pptxgenjs.md) that consume significant tokens
