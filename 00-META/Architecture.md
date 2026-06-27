---
title: Obsidian Vault — Knowledge Architecture
created: 2026-06-27
tags: [meta, vault, architecture, index]
status: active
aliases: [Knowledge Vault, Vault Architecture]
---

# Obsidian Vault — Architecture Path

> This vault at `/root/projects//` is the shared knowledge layer.
> Designed for compounding: every note, every link, every day increases value.

## Vault Root

```
/root/projects/obsidian-vault/
```

**Access**: Filesystem tools (read_file, write_file, search_files, patch).
No Obsidian app or MCP server required for core functionality.

## Core Conventions

| Convention | Rule | Why |
|------------|------|-----|
| **YAML Frontmatter** | Every `.md` file starts with `---` title/tags/status/aliases | Agent parseable |
| **Wikilinks** | `[[Note Name]]` for all cross-references | Graph relationships |
| **Tags** | Hyphenated: `#agent`, `#pattern`, `#lesson`, `#decision` | Discoverable |
| **LINK Headers** | Every note has `> Used by → [[...]]` and `→ [[...]]` at top | Backlink discovery |
| **Status** | `active`, `draft`, `complete`, `superseded` | Filter by state |
| **Aliases** | Alternate names for wikilinks | Multiple entry points |

## How Agents Use This Vault

### Reading (discovery)
1. `search_files(pattern, path="/root/projects/obsidian-vault/")` — find relevant notes
2. `read_file(path)` — read full note content
3. Follow wikilinks in notes for deep traversal
4. Check frontmatter `status` for filter
5. Use LINK headers for reverse discovery

### Writing (contributing)
1. Find correct folder (00-META, 10-PROPERTIES, 20-AGENTS, 30-PATTERNS, 40-LOGS, 50-ARCHIVE)
2. Create note with full frontmatter
3. Add LINK header: `> Part of → [[Parent Note]]` and `→ [[Related Note]]`
4. Use wikilinks throughout content
5. After creation, update parent's file to link back (bidirectional linking)

### Daily Notes
1. CoS creates `40-LOGS/YYYY-MM-DD.md` from [[40-LOGS/_Template|]]
2. Each note captures, priority, blockers, decisions, deferred
3. Daily notes are the signal source for compounding

## Folder Semantics

| Folder | Content | Owner |
|--------|---------|-------|
| `00-META/` | Dashboards, indexes, vault index | CoS |
| `10-PROPERTIES/` | Per-property docs (Story Engine, OctoGentic, Bookbrary, RoleFresh) | CoS + property agents |
| `20-AGENTS/` | Agent definitions, objective functions, delegation maps | CoS |
| `30-PATTERNS/` | Cross-agent patterns (compounding, self-healing, etc.) | Any agent |
| `40-LOGS/` | Daily standups, retros | CoS |
| `50-ARCHIVE/` | Superseded, completed | CoS |

## Compounding Metrics Dashboard

Tracked in → [[30-PATTERNS/Compounding-Knowledge]]

| Metric | Current | 30-day Target |
|--------|---------|---------------|
| Total notes | ~25 | 100+ |
| Total wikilinks | ~60 | 500+ |
| Backlinks per note | avg 2 | avg 5 |
| Cross-property connections | ~10 | 50+ |
| Daily note streak | 1 day | 30 days |
| Agent query sessions/week | 0 habitual yet | 20+ |

## Why Not a Database?

| Approach | Pros | Cons |
|----------|------|------|
| **This vault (flat MD)** | Full栾t, readable, git-trackeable, zero infra | No concurrent write safety, no rich queries |
| Supabase DB | Concurrent, queryable, structured | Requires schema, not human-editable, no wiki graph |
| Graph DB | Relationship queries | Overkill, maintenance burden, no content |

**Flat markdown wins** because: agents read/write files natively, humans edit with any text editor, git tracks history, zero infrastructure. If we need structured query later, we parse frontmatter (which we already have).

## Future Enhancements

- [ ] **Obsidian Desktop + MCP**: If GUI available, obsidian-mcp-plugin adds graph traversal tools
- [ ] **Dataview queries**: Parse YAML scale for agent dashboards
- [ ] **Git hooks**: Auto-update indexes on commit
- [ ] **Cron-derived daily notes**: Auto-generate from cron outputs
- [ ] **Semantic search**: Embed notes for vector search when scale demands

## Quick Start for New Agents

1. Read this note
2. Read [[00-META/Home]] for dashboard
3. Read [[Agent Objective Functions]] for your scoring
4. Check [[40-LOGS/]] for today's context
5. When you learn something: write to appropriate folder, link to related, update dashboard
