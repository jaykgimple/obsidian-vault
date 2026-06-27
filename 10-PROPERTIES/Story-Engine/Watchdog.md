---
title: Story Engine — Watchdog & Recovery
created: 2026-06-27
tags: [story-engine, watchdog, recovery, self-healing]
status: active
aliases: [Watchdog, Queue Worker, Self-Healing]
---

# Story Engine — Watchdog & Recovery

> Self-healing infrastructure for the generation pipeline.
> Pattern: → [[Pattern: Self-Healing Pipelines]]
> Part of → [[10-PROPERTIES/Story-Engine/Overview]]

## Watchdog (`scripts/watchdog.py`)

| Aspect | Detail |
|--------|--------|
| **Poll interval** | 60s |
| **Checks** | Engine process alive? Supabase queue orphaned items? |
| **Recovery** | Restart engine if dead; reset stale `processing` items |
| **Backoff** | `r^1.5 × base_wait` (exponential with dampening) |
| **Alert** | After max retries exhausted |

## Queue Worker (`scripts/queue_worker.py`)

| Aspect | Detail |
|--------|--------|
| **Poll interval** | 900s (15 min) |
| **Poll filter** | `status: pending` + stale `processing` (>30min) |
| **Recovery** | Reuse existing local series (no duplicates) |
| **Processing** | Marks Supabase + SQLite, processes, updates status |

## Stale Recovery Logic

```
1. Fetch queue items where status = "pending"
2. Also fetch status = "processing" AND started_at < (now - 30min)
3. For each stale item:
   a. Check if engine process is running (PID alive?)
   b. If engine dead → reset to "pending" → watchdog will restart
   c. If engine alive but item stale → reset to "pending" → worker re-picks
```

## Lessons Learned

| Issue | Fix | Lesson Note |
|-------|-----|-------------|
| Stale `processing` never recovered | Added stale fetch to `poll_queue()` | → [[Lesson: Dual Queue Desync]] |
| Dual queue desync (Supabase ≠ SQLite) | Reuse existing local series | → [[Lesson: Dual Queue Desync]] |
| `langchain-openai` missing | `pip install langchain-openai` | → [[10-PROPERTIES/Story-Engine/Lessons/]] |
| Cover not uploaded | Always call `_upload_cover_to_supabase()` | → [[Lesson: Cover Upload Gap]] |
| Chapter content empty in Supabase | Backfill from `manuscript_chunks` | → [[Lesson: Chapter Content Backfill]] |
| Review saves failed | Wrong service key (anon vs service role) | → [[Lesson: Service Key Required]] |
