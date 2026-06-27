---
title: Self-Healing Pipelines
created: 2026-06-27
tags: [pattern, self-healing, reliability]
status: active
aliases: [Pattern: Self-Healing Pipelines, Watchdog Pattern]
---

# Self-Healing Pipelines

> Detect failures, recover automatically, escalate only when truly stuck.
> Used by → [[Story Engine — Overview]], → [[Agent: Pipeline Orchestrator]]

## When To Use
- Queue-based processing (book generation)
- Multi-agent pipelines
- Any system that must not silently stall

## Core Mechan. Poll → detect stuck items
2. Check: is the worker alive?
3. Check: is the engine running?
4. If engine dead + item stale > 30min → reset to pending
5. If worker dead + item stale → kill worker, start new
6. Escalate: if recovery fails after 2 attempts → alert human
```

## Story Engine Implementation

| Component | Role | Self-Heal Action |
|-----------|------|------------------|
| Watchdog (60s poll) | Health check | Restart engine if dead |
| Queue Worker (900s poll) | Processing | Reset stale items |

### Watchdog Loop (every 60s)
- Check engine process alive → if dead, check restart policy
- Check Supabase queue for orphaned `processing` items → reset to `pending`
- Check restart `r` counter → apply backoff `r^1.5 × base_wait`
- Alert human only after exhausting automated recovery

### Key Fixes Applied (2026-06)
- `poll_queue()` now fetches stale `processing` (>30min) + `pending`
- Watchdog checks Supabase queue for orphaned items
- Circuit breaker stops after max retries (prevents infinite loop)
- `langchain-openai` dependency added (was missing, silent crash)

### Known Pitfalls
- → [[Lesson: Dual Queue Desync]] — Supabase + SQLite must stay in sync→ [[Lesson: Rate Limit Management]] — daily quota exhausted → wait for reset
- Dual workers running simultaneously → duplicate processing risk

## Connection To Compounding

Self-healing IS signal generation:
- Every failure detected = one signal
- Every signal = potential pattern note
- Every pattern note = preventing future failures

→ [[Pattern: Compounding Knowledge]]

## Compounding Metrics

| Metric | Source | Signal |
|--------|--------|--------|
| Failure rate | Watchdog logs | High = pattern needed |
| Recovery speed | Queue timestamps | Slow = better detection |
| False positive rate | Escalation logs | High = threshold tuning |
