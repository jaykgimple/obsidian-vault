---
title: Lesson: Coherence Threshold Must Be 9
created: 2026-06-27
tags: [lesson, story-engine, coherence]
status: active
---

# Lesson: Coherence Threshold Must Be 9

> Threshold 7 let through contradictions. Threshold 9 catches real problems.

## What Happened
- Original threshold: 7/10 passes
- Result: Characters teleporting, contradictory facts, pronoun shifts in published books
- User feedback: "it is all over the place"

## Root Cause
- Low threshold allowed segments with location contradictions to pass
- Novelist had no awareness of prior segment content beyond 400 chars

## Fix Applied
- → [[Agent: Dev Editor]] threshold raised: 7 → 9
- Max revisions increased: 2 → 4
- `get_story_state()` added: builds running context document for novelist

## Evidence (from → [[Pattern: Review-and-Revision]] first pass)
- 200+ chapters reviewed at threshold 9
- Only 6/200 passed on first try (rest failed at threshold 7 level too)
- Clear improvement trajectory visible in threshold 9 pass rate after revision
