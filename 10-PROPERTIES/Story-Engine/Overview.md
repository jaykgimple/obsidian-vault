---
title: Story Engine — Architecture Overview
created: 2026-06-27
tags: [property, story-engine, pipeline]
status: active
aliases: [Story Engine, Book Generation Pipeline]
---

# Story Engine

> AI agentic book generation pipeline. 6 specialized agents produce 52-segment novels with coherence scoring.
> Property of → [[OctoGentic — Portfolio]]

## Stack
- **Runtime**: Python 3, 64K context window
- **Entry point**: `main.py run-all`
- **Queue**: Supabase `generation_queue` + SQLite `generation_queue`
- **Storage**: Supabase (books, chapters)
- **Frontend**: → [[Bookbrary — Reader Frontend]]

## Pipeline Flow

```
User submits series (→ [[Bookbrary — Submission Form]])
  → Worker picks up queue item (→ [[Story-Engine — Queue Worker]])
    → Architect defines outline & arc
      → Biographer generates chapter prose drafts
        → Novelist writes segment prose (with → [[Pattern: Compounding Knowledge]] context)
          → Dev Editor scores consistency (≥9/10)
            → Copy Editor final polish
              → Push to Supabase
```

## Key Agents
- → [[Agent: Architect]]
- → [[Agent: Novelist]]
- → [[Agent: Dev Editor]]
- → [[Agent: Biographer]]
- → [[Agent: Copy Editor]]
- → [[Agent: Audit]]
- → [[Agent: Pipeline Orchestrator]]

## Lessons Learned
- → [[Lesson: Coherence Threshold Must Be 9]]
- → [[Lesson: Chapter Content Backfill]]
- → [[Lesson: Cover Upload Gap]]
- → [[Lesson: Dual Queue Desync]]

## Related Patterns
- → [[Pattern: Self-Healing Pipelines]]
- → [[Pattern: Coherence Scoring]]
- → [[Pattern: Queue Dual-Write]]
- → [[Pattern: Review-and-Revision]]
