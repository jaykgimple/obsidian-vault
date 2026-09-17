---
title: Lesson: Gender Anchor FIXED + Talen pronoun drift was widespread
created: 2026-09-13
tags: [lesson, story-engine, continuity, pronoun, fix]
status: active
---

# Lesson: Character DNA gender anchor FIXED (root cause #1 resolved)

> Follow-up to [[10-PROPERTIES/Story-Engine/Lessons/Gender-Anchor-Object-Desync|Gender-Anchor-Object-Desync]]. This tick IMPLEMENTED the gender fix.

## Scope discovered (worse than B1Ch9Seg3 alone)

The Talen pronoun drift was NOT one segment. Strong-signal scan across all
completed series-3 segments found Talen misgendered (she/her) in 5 segments:

- B1Ch8Seg4 (id 2443) — "her silhouette" / "She looked" / "She stared"
- B1Ch9Seg2 (id 2445) — "her hands" / "her jaw"
- B1Ch9Seg4 (id 2447) — "She had her own blade drawn"
- B1Ch10Seg1 (id 2448) — "her hand" / "her steps"
- B1Ch10Seg2 (id 2449) — "She wasn't looking at them"

Plus the 2 already-'error' segments (B1Ch9Seg1 object-holder, B1Ch9Seg3 pronoun).
= 7 defective segments in book 1.

## Root cause

`story_dna` character JSON has NO `gender`/`pronouns` field. The name "Talen" is
gender-ambiguous, so the novelist flips he/she ~50% of the time. The fact-checker
had no deterministic anchor either (inferred from already-contaminated prose),
so it caught it once (B1Ch9Seg3) and let 5+ others through as 'completed'.

## Fix implemented (engine, tested 66 tests OK)

1. `agents/architect.py` — character schema now requests `gender` field (future series).
2. `core/context.py` — new `pronouns_for(char)` helper (maps gender -> he/him, she/her, they/them).
3. `agents/biographer.py` — "CHARACTER NAMES + PRONOUNS" block now emits `Name (he/him)`
   in the high-recall end position of the novelist context (can never be truncated).
4. `agents/fact_checker.py` — "Characters" block now emits `[pronouns: he/him]` so the
   pronoun check is deterministic instead of inferred.
5. Backfilled `gender` into series-3 DNA: Bryn=female; Kael/Kester/Talen/Valerius=male.

## Actions taken

- Killed the stale run (old code would keep misgendering Talen through books 2-3).
- Marked the 5 misgendered segments 'error' (so `_qc_scan_and_fix` force-regenerates
  them through the full novelist pipeline with the new pronoun anchor).
- Reset chapters 8/10 to 'generating' (ch9 already pending).
- Relaunched `run-all --series-id 3` with fixed code. Phase-0 QC scan regenerates
  the 7 error segments first, then continues books 2-3 clean.

## STILL OPEN (deferred, documented in parent note)

- Object-holder alias: `the_gauntlet` vs `the_ornate_gauntlet` vs `the_second_gauntlet`
  are separate world-state entities → false holder contradictions (B1Ch9Seg1). Needs
  entity canonicalization/aliasing. May resolve itself this run; verify after regen.
- Divergent-scene prevention (sequel beats + continuity handoff) — still open.