---
title: Story Engine — Pipeline Architecture
created: 2026-06-27
tags: [story-engine, pipeline, architecture]
status: active
aliases: [Generation Pipeline, Engine Architecture]
---

# Story Engine — Pipeline Architecture

> The full generation pipeline: queue → architect → biographer → novelist → dev_editor → copy_editor → audit → push.
> Part of → [[10-PROPERTIES/Story-Engine/Overview]]

## Pipeline Flow

```
[Queue: Supabase generation_queue]
    ↓
[1. Architect Agent] → Series config, chapter outlines, story DNA
    ↓
[2. Biographer Agent] → Chapter draft prose (~300w)
    ↓
[3. Novelist Agent] → Segment prose (~800w) with → [[Pattern: Coherence-Scoring]] context
    ↓
[4. Dev Editor Agent] → Consistency review (≥9 threshold)
    ↓ (if <9: revision loop, max 4 attempts)
[5. Copy Editor Agent] → Grammar, style, final polish
    ↓
[6. Audit Agent] → Verify covers, titles, summaries, completeness
    ↓
[Push to Supabase] → Books, chapters, covers → Bookbrary UI
```

## Key Files

| File | Role |
|------|------|
| `main.py` | Entry point (`run-all`, `run-worker`) |
| `pipeline/engine.py` | Pipeline orchestration, revision loop |
| `agents/architect.py` | Series/chapter design |
| `agents/biographer.py` | Chapter draft generation |
| `agents/novelist.py` | Segment prose (with story_state) |
| `agents/dev_editor.py` | Consistency scoring |
| `agents/copy_editor.py` | Grammar/polish |
| `agents/audit.py` | Final verification + auto-fix |
| `scripts/queue_worker.py` | Queue polling + stale recovery |
| `scripts/watchdog.py` | Health check + engine restart |
| `scripts/review_series.py` | Post-generation review + revision |

## Generation Stats (per book)

| Metric | Value |
|--------|-------|
| Segments | 52 |
| Chapters | ~13 |
| Words | ~26,000 |
| LLM requests | ~1,000+ |
| Time | ~30-60 min |

## Compounding Integration

- `get_story_state(series_id)` builds running context → [[Pattern: Coherence-Scoring]]
- Revision loop → [[Pattern: Review-and-Revision]]
- Watchdog + queue worker → [[Pattern: Self-Healing Pipelines]]
- Lessons from failures → [[10-PROPERTIES/Story-Engine/Lessons/]]
