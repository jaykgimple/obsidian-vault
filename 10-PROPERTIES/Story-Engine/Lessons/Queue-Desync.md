---
title: Lesson: Dual Queue Desync
created: 2026-06-27
tags: [lesson, story-engine, ops]
status: active
---

# Lesson: Dual Queue Desync

> Supabase + SQLite queues must stay in sync, or items get lost.

## What Happened
- Story engine uses TWO queues: Supabase `generation_queue` + SQLite `generation_queue`
- Worker marked item `processing` in Supabase → crashed
- New worker only polled `pending` → stuck item never recovered
- SQLite had different state than Supabase

## Root Cause
- No stale-`processing` recovery
- Dual write without recon## Fix Applied
- `poll_queue()` nowprocessing` (>30min) + `pending`
-_queue_processing()` updates both queues atomically
- Worker heartbeat tracked; zombie items auto-reset

## Lesson
If you have two sources of truth:
1. Pick ONE as primary (Supabase)
2. Sync writes immediately
3. Reconcile on read
4. Recover from divergence

→ [[Pattern: Self-Healing Pipelines]] | → [[Pattern: Compounding Knowledge]]
