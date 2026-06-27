---
title: Story Engine — Review System
created: 2026-06-27
tags: [story-engine, review, post-generation]
status: active
aliases: [Post-Generation Review, Chapter Review]
---

# Story Engine — Review System

> Post-generation chapter review with auto-revision.
> Script: `scripts/review_series.py`
> Pattern: → [[Pattern: Review-and-Revision]]
> Part of → [[10-PROPERTIES/Story-Engine/Overview]]

## Review Pipeline

```
1. Pull chapter content from Supabase (via REST API, service role key)
2. Build story state (→ [[Pattern: Coherence-Scoring]])
3. Run dev_editor review → consistency score (1-10)
4. If < 9: revise via novelist agent (max 4 attempts)
5. Re-review revised content
6. Save to Supabase if ≥ 9
7. Mark chapter as "revised"
```

## Review Results (2026-06 First Pass)

| Series | Chapters | Passed | Failed | Save Failures |
|--------|----------|--------|--------|---------------|
| Forged Memories | 30 | ~5 | ~25 | ~8 |
| Algetasadoria | 54 | ~2 | ~52 | ~15 |
| The Last Ural Owl | 13 | ~1 | ~12 | ~3 |
| Chrono-Compass | 32 | ~3 | ~29 | ~12 |
| **Total** | **~129** | **~11** | **~118** | **~38** |

**Save failures**: All caused by wrong service key (anon vs service role). Bug fixed.

## Common Failure Patterns

| Pattern | Frequency | Root Cause |
|---------|-----------|------------|
| Location teleport | Very High | Novelist lacks position tracking → fixed with story_state |
| Contradictory new info | High | Characters inventing facts not in story_state |
| POV/tense shift | Medium | No consistent voice in prompt |
| Mid-sentence truncation | Medium | Max_tokens too low for long chapters |
| Pronoun inconsistency | Low | Character gender not tracked |

## Compounding Loop

Review → Pattern found → Lesson note created → Agent prompt updated → Fewer failures next time.

→ [[30-PATTERNS/Compounding-Knowledge]]
