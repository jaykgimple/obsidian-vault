---
title: Review and Revision
created: 2026-06-27
tags: [pattern, review, revision]
status: active
aliases: [Pattern: Review-and-Revision, Post-Generation Review]
---

# Review and Revision

> Post-generation quality gate: audit, score, revise, repeat.
> Script: `scripts/review_series.py`
> Used by → [[Story Engine — Overview]]

## Why Separate Review from Generation?

- Generation optimizes forward progress
- Review optimizes quality
- Mixing them creates conflicts (go fast vs. go perfect)
- Dedicated review catches what generation missed

## Review Pipeline

```
1. Pull chapter content from Supabase
2. Build story state (all prior chapter summaries + last 3 segments)
3. Run dev_editor review (→ [[Pattern: Coherence Scoring]])
4. If score < 9: revise via novelist agent
5. Re-review revised content
6. Save to Supabase (only if score ≥ 9)
7. Mark chapter as "revised"
```

## Two Review Modes

| Mode | Trigger | Scope |
|------|---------|-------|
| **Inline** | During generation | Current segment vs prior segment |
| **Post-generation** | After book completes | ALL chapters cross-referenced |

## Key Lessons (2026-06)

- **Wrong service key**: Write operations need service role key, not anon → [[Lesson: Service Key Required]]
- **Truncation**: LLM output gets cut off mid-sentence for long chapters → need chunking
- **Rate limits**: Reviewing 200+ chapters consumes 1000+ LLM calls → batch carefully
- **Speed ≠ Quality**: First review pass catches ~60% of issues; revision catches 30% more

## Compounding Loop

Review finds patterns → Pattern notes inform agent prompts → Prompts improve generation → Less to review → Costs drop → Value increases.
