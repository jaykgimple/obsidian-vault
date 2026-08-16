---
title: Story Engine — Architecture Overview
created: 2026-06-27
tags: [property, story-engine, pipeline]
status: active
aliases: [Story Engine, Book Generation Pipeline, Story Engine — Overview]
---

# Story Engine

> AI agentic book generation pipeline. 6 specialized agents produce 52-segment novels with coherence scoring.
> Property of → [[Overview]]

## Stack
- **Runtime**: Python 3, 64K context window
- **Entry point**: `main.py run-all`
- **Queue**: Supabase `generation_queue` + SQLite `generation_queue`
- **Storage**: Supabase (books, chapters)
- **Frontend**: → [[Bookbrary]]

## Pipeline Flow

```
User submits series (→ [[Bookbrary|Bookbrary Submission Form]])
  → Worker picks up queue item (→ [[Pipeline|Story-Engine Queue Worker]])
    → Architect defines outline & arc
      → Biographer generates chapter prose drafts
        → Novelist writes segment prose (with → [[Compounding-Knowledge]] context)
          → Dev Editor scores consistency (≥9/10)
            → Copy Editor final polish
              → Push to Supabase
```

## Key Agents
- → [[Story-Engine/Objectives#Agent: Architect|Agent: Architect]]
- → [[Story-Engine/Objectives#Agent: Novelist|Agent: Novelist]]
- → [[Story-Engine/Objectives#Agent: Development Editor|Agent: Dev Editor]]
- → [[Agents|Agent: Biographer]]
- → [[Story-Engine/Objectives#Agent: Copy Editor|Agent: Copy Editor]]
- → [[Story-Engine/Objectives#Agent: Audit Agent|Agent: Audit]]
- → [[Story-Engine/Objectives#Agent: Pipeline Orchestrator|Agent: Pipeline Orchestrator]]

## Lessons Learned
- → [[Coherence-9]]
- → [[Chapter-Backfill]]
- → [[Cover-Upload]]
- → [[Queue-Desync]]

## Related Patterns
- → [[Self-Healing-Pipelines]]
- → [[Coherence-Scoring]]
- → [[Self-Healing-Pipelines|Pattern: Queue Dual-Write]]
- → [[Review-and-Revision]]
