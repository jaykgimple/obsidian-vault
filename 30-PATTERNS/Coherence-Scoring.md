---
title: Coherence Scoring
created: 2026-06-27
tags: [pattern, coherence, quality]
status: active
aliases: [Pattern: Coherence Scoring, Consistency Gate]
---

# Coherence Scoring

> Numeric score (1-10) measuring whether a segment contradicts established facts.
> Owned by → [[Agent: Dev Editor]]
> Used in → [[Story Engine — Overview]], → [[Story Engine — Review System]]

## Scoring Criteria

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Location/POSITION | 25% | Character positions match prior segments |
| POV/Tense/Voice | 25% | No unexplained POV or tense shifts |
| Prior Event Accuracy | 25% | No contradictions with established facts |
| Character Details | 15% | Appearance, status, equipment consistent |
| World Rules | 10% | No breaking established world rules |

## Thresholds

| Score | Action |
|-------|--------|
| ≥ 9 | PASS — Continue to copy editor |
| 7-8.9 | FAIL → Auto-revise by novelist (max 4 attempts) |
| < 7 | FAIL → Hard fail, escalate |

## Current Implementation
- `agents/dev_editor.py` → `consistency` score field
- `pipeline/engine.py` → revision loop triggers when < 9
- Max 4 revision attempts before human escalation
- `get_story_state(series_id)` → builds context document for novelist

## Common Failure Modes (2026-06 Review)

From → [[Story Engine — Review System]] review of 200+ chapters:

| Failure Type | Frequency | Root Cause | Fix Applied |
|-------------|-----------|------------|-------------|
| Location teleport | High | Novelist lacks position tracking | → [[Pattern: Compounding Knowledge]] story_state |
| POV/tense shift | Medium | No consistent voice in prompt | Dev_editor check added |
| Contradictory new info | High | Characters inventing facts not in story_state | story_state builder + check |
| Mid-sentence truncation | Medium | Max_tokens too low for chapter output | Increased + chunking |
| Pronoun inconsistency | Low | Character gender not tracked | story_state character registry |

## Compounding Angle

Each coherence failure generates a signal:
- What failed? → Logged in review output
- What pattern? → Create/update [[10-PROPERTIES/Story-Engine/Lessons|Lesson]] note
- What fix? → Update novelist prompt or story_state builder

→ More reviews → More patterns → Better prompts → Fewer failures → Compounding.
