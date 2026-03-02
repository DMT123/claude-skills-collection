# Claude Skills Collection

A comprehensive collection of **64 skills** for Claude Code / Cowork, organized by source.

## Structure

```
├── core/           # Built-in Anthropic skills (13 skills)
├── plugins/        # Official plugin skills (49 skills)
├── marketplace/    # Marketplace skills (2 skills)
└── templates/      # Reusable CLAUDE.md templates + GitHub configs
```

## Templates & Cross-Project Configs

The `templates/` directory contains reusable configs for any new project. See [templates/GUIDE.md](templates/GUIDE.md) for full details.

| Template | Purpose |
|----------|---------|
| [CLAUDE.md.template](templates/CLAUDE.md.template) | Standard project CLAUDE.md |
| [CLAUDE.monorepo.md.template](templates/CLAUDE.monorepo.md.template) | Monorepo CLAUDE.md |
| [CLAUDE.local.md.template](templates/CLAUDE.local.md.template) | Personal overrides (gitignored) |
| [global-CLAUDE.md.template](templates/global-CLAUDE.md.template) | Global user defaults (`~/.claude/CLAUDE.md`) |
| [MEMORY-GUIDE.md](templates/MEMORY-GUIDE.md) | How CLAUDE.md hierarchy works as persistent memory |
| [API-KEYS-GUIDE.md](templates/API-KEYS-GUIDE.md) | Secure central API key management |
| [env.master.template](templates/env.master.template) | Master API key vault template |
| [.github/](templates/.github/) | CI workflow, PR template, issue templates, Dependabot |
| [.editorconfig](templates/.editorconfig) | Consistent formatting across editors |
| [.gitignore.template](templates/.gitignore.template) | Comprehensive gitignore |

## Core Skills

| Skill | Description |
|-------|-------------|
| [algorithmic-art](core/algorithmic-art/) | Algorithmic art using p5.js with seeded randomness and interactive parameter exploration |
| [brand-guidelines](core/brand-guidelines/) | Applies Anthropic's official brand colors and typography |
| [canvas-design](core/canvas-design/) | Create visual art in .png and .pdf documents using design philosophy |
| [docx](core/docx/) | Word document creation, editing, and analysis |
| [internal-comms](core/internal-comms/) | Internal communications: status reports, newsletters, FAQs, incident reports |
| [mcp-builder](core/mcp-builder/) | Guide for creating MCP servers (Python FastMCP / Node MCP SDK) |
| [pdf](core/pdf/) | PDF manipulation: extract text/tables, create, merge, split, handle forms |
| [pptx](core/pptx/) | PowerPoint presentation creation, editing, and analysis |
| [schedule](core/schedule/) | Create scheduled tasks that run on demand or on an interval |
| [skill-creator](core/skill-creator/) | Create, modify, improve, and evaluate skills |
| [slack-gif-creator](core/slack-gif-creator/) | Animated GIFs optimized for Slack |
| [theme-factory](core/theme-factory/) | Styling toolkit with 10 pre-set themes for slides, docs, HTML, etc. |
| [xlsx](core/xlsx/) | Excel spreadsheet creation, editing, and analysis |

## Plugin Skills

### Coderabbit
| Skill | Description |
|-------|-------------|
| [code-review](plugins/coderabbit/code-review/) | AI code review with autonomous fix-review cycles |

### Claude MD Management
| Skill | Description |
|-------|-------------|
| [claude-md-improver](plugins/claude-md-management/claude-md-improver/) | Audit and improve CLAUDE.md files in repositories |

### Firecrawl
| Skill | Description |
|-------|-------------|
| [firecrawl-cli](plugins/firecrawl/firecrawl-cli/) | Web scraping and crawling with LLM-optimized output |

### Frontend Design
| Skill | Description |
|-------|-------------|
| [frontend-design](plugins/frontend-design/) | Production-grade frontend interfaces with high design quality |

### Hookify
| Skill | Description |
|-------|-------------|
| [writing-rules](plugins/hookify/writing-rules/) | Create and configure hookify rules |

### Hugging Face (9 skills)
| Skill | Description |
|-------|-------------|
| [hf-mcp](plugins/huggingface/hf-mcp/) | Hugging Face Hub via MCP server tools |
| [hugging-face-cli](plugins/huggingface/hugging-face-cli/) | Hub operations using the `hf` CLI |
| [hugging-face-datasets](plugins/huggingface/hugging-face-datasets/) | Create and manage datasets on HF Hub |
| [hugging-face-evaluation](plugins/huggingface/hugging-face-evaluation/) | Evaluation results in model cards |
| [hugging-face-jobs](plugins/huggingface/hugging-face-jobs/) | Run workloads on HF Jobs infrastructure |
| [hugging-face-model-trainer](plugins/huggingface/hugging-face-model-trainer/) | Train/fine-tune LLMs with TRL on HF Jobs |
| [hugging-face-paper-publisher](plugins/huggingface/hugging-face-paper-publisher/) | Publish research papers on HF Hub |
| [hugging-face-tool-builder](plugins/huggingface/hugging-face-tool-builder/) | Build tools using HF API data |
| [hugging-face-trackio](plugins/huggingface/hugging-face-trackio/) | Track ML training experiments with Trackio |

### Notion (4 skills)
| Skill | Description |
|-------|-------------|
| [knowledge-capture](plugins/notion/knowledge-capture/) | Transform conversations into structured Notion documentation |
| [meeting-intelligence](plugins/notion/meeting-intelligence/) | Prepare meeting materials from Notion context |
| [research-documentation](plugins/notion/research-documentation/) | Synthesize Notion workspace findings into research docs |
| [spec-to-implementation](plugins/notion/spec-to-implementation/) | Turn specs into concrete Notion tasks |

### Playground
| Skill | Description |
|-------|-------------|
| [playground](plugins/playground/) | Interactive single-file HTML explorers with live preview |

### Plugin Dev (7 skills)
| Skill | Description |
|-------|-------------|
| [agent-development](plugins/plugin-dev/agent-development/) | Create agents for Claude Code plugins |
| [command-development](plugins/plugin-dev/command-development/) | Create slash commands for Claude Code |
| [hook-development](plugins/plugin-dev/hook-development/) | Create hooks (PreToolUse, PostToolUse, Stop, etc.) |
| [mcp-integration](plugins/plugin-dev/mcp-integration/) | Integrate MCP servers into plugins |
| [plugin-settings](plugins/plugin-dev/plugin-settings/) | Plugin configuration with .local.md files |
| [plugin-structure](plugins/plugin-dev/plugin-structure/) | Plugin directory layout and manifest config |
| [skill-development](plugins/plugin-dev/skill-development/) | Create skills for Claude Code plugins |

### PostHog
| Skill | Description |
|-------|-------------|
| [posthog-instrumentation](plugins/posthog/posthog-instrumentation/) | Add PostHog analytics instrumentation to code |

### Sentry (5 skills)
| Skill | Description |
|-------|-------------|
| [sentry-code-review](plugins/sentry/sentry-code-review/) | Analyze Sentry comments on GitHub PRs |
| [sentry-setup-ai-monitoring](plugins/sentry/sentry-setup-ai-monitoring/) | Setup Sentry AI Agent Monitoring |
| [sentry-setup-logging](plugins/sentry/sentry-setup-logging/) | Setup Sentry structured logging |
| [sentry-setup-metrics](plugins/sentry/sentry-setup-metrics/) | Setup Sentry custom metrics |
| [sentry-setup-tracing](plugins/sentry/sentry-setup-tracing/) | Setup Sentry performance monitoring |

### Superpowers (14 skills)
| Skill | Description |
|-------|-------------|
| [brainstorming](plugins/superpowers/brainstorming/) | Explore intent, requirements, and design before implementation |
| [dispatching-parallel-agents](plugins/superpowers/dispatching-parallel-agents/) | Run 2+ independent tasks in parallel |
| [executing-plans](plugins/superpowers/executing-plans/) | Execute implementation plans with review checkpoints |
| [finishing-a-development-branch](plugins/superpowers/finishing-a-development-branch/) | Guide completion of dev work (merge, PR, cleanup) |
| [receiving-code-review](plugins/superpowers/receiving-code-review/) | Handle code review feedback with technical rigor |
| [requesting-code-review](plugins/superpowers/requesting-code-review/) | Verify work meets requirements before merging |
| [subagent-driven-development](plugins/superpowers/subagent-driven-development/) | Execute plans with independent tasks via subagents |
| [systematic-debugging](plugins/superpowers/systematic-debugging/) | Debug bugs and test failures systematically |
| [test-driven-development](plugins/superpowers/test-driven-development/) | Write tests before implementation code |
| [using-git-worktrees](plugins/superpowers/using-git-worktrees/) | Isolated git worktrees for feature work |
| [using-superpowers](plugins/superpowers/using-superpowers/) | Find and use skills effectively |
| [verification-before-completion](plugins/superpowers/verification-before-completion/) | Run verification before claiming work is done |
| [writing-plans](plugins/superpowers/writing-plans/) | Plan multi-step tasks before coding |
| [writing-skills](plugins/superpowers/writing-skills/) | Create and verify new skills |

### Vercel (3 skills)
| Skill | Description |
|-------|-------------|
| [deploy](plugins/vercel/deploy/) | Deploy applications to Vercel |
| [logs](plugins/vercel/logs/) | View Vercel deployment logs |
| [setup](plugins/vercel/setup/) | Set up Vercel CLI and project config |

## Marketplace Skills

### Customer Support
| Skill | Description |
|-------|-------------|
| [customer-research](marketplace/customer-support/customer-research/) | Research customer questions across docs and knowledge bases |
| [knowledge-management](marketplace/customer-support/knowledge-management/) | Write and maintain KB articles from resolved support issues |

## Usage

Each skill folder contains a `SKILL.md` file with the full skill definition, including YAML frontmatter (name, description, triggers) and the skill's instructions. Some skills include additional reference files, examples, or sub-resources.

Collected on 2026-03-02 from Claude Code / Cowork environment.
