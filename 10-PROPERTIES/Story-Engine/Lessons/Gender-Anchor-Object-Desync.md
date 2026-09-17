---
title: Lesson: Character DNA Lacks Gender Anchor (pronoun drift)
created: 2026-09-13
tags: [lesson, story-engine, continuity, divergent-scene]
status: active
---

# Lesson: Forged Memories B1Ch9 surfaced 3 continuity root-causes

> Run: series_id=3 ("Forged Memories"). 2 segments marked 'error', non-blocking.
> Related: → [[10-PROPERTIES/Story-Engine/Overview|Story Engine]] ← [[10-PROPERTIES/Story-Engine/Pipeline]] ← [[10-PROPERTIES/Story-Engine/Lessons/Gender-Anchor-FIXED|Gender Anchor FIXED]]

## Findings (segment ids + one-line quote)

1. **B1Ch9Seg3 (id 2446) error — pronoun drift:**
   - "Talen had pivoted toward the sound, her hands empty..." (Talen is male in bible)
   - Root: `story_dna` for "Talen Greyhue" has NO gender/pronoun field. Novelist has no anchor, flips he/she.

2. **B1Ch9Seg1 (id 2444) error + gauntlet desync:**
   - World-state flagged "gauntlet holder = on the slate floor (dropped) @ B1Ch8Seg3" while story needs Bryn to carry it.
   - Root: `world_state` has TWO entities for the same object: `the_ornate_gauntlet` (holder=Kester, B1Ch5) vs `the_gauntlet` (holder=Bryn). No alias/canonicalization → false holder contradictions.

3. **Divergent scene (documented bug, prevention NOT implemented):**
   - B1Ch9Seg1 continuity = "abandoned waystation root cellar"; B1Ch9Seg2/Seg4 = "Echo Caves". Two divergent escape branches.
   - B1Ch10Seg1 prose = "hauling her deeper into the Echo Caves" but GEOGRAPHY label = "Burned District".

## Root-Cause Fixes Needed (engine, not prose)

- Character DNA schema: add explicit `gender`/`pronouns` field; fact-checker enforces pronoun == canonical gender.
- world_state: entity identity/alias canonicalization (merge "gauntlet" + "ornate gauntlet").
- Divergent-scene prevention (enforce sequel beats + correct continuity handoff location) — still open.

## Status
- Run healthy (alive, progressing ~40/120, avg 8.0). Errors are non-blocking by design; must regenerate the 2 segments + fix root cause before "clean completion" is valid.