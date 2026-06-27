---
title: Story Engine — Agentic Objectives
created: 2026-06-27
tags: [story-engine, agents, objectives]
status: active
aliases: [Story Engine Agent Objectives, Book Generation Agent Scoring]
---

# Story Engine — Agentic Objectives

> Source: `story-engine/AGENTIC_OBJECTIVES.md`
> Part of → [[10-PROPERTIES/Story-Engine/Overview]]
> Related: → [[Agent Objective Functions]], → [[Story Engine — Agent Deep-Dives]]

## Agent: Architect

| Aspect | Detail |
|--------|--------|
| **Purpose** | Design series structure: books, chapters, story DNA, character arcs |
| **Optimizes for** | Narrative coherence (consistent world-building, character arcs that pay off), not speed |
| **Success metric** | Continuity alert rate (fewer alerts = better planning); chapter completion rate |
| **Anti-pattern** | Contradictory world rules; character arcs that go nowhere; plot holes |
| **Quality gate** | Every chapter must have: goal, conflict, disaster, reaction, dilemma, decision |
| **Objective function** | `continuity_score × 0.4 + chapter_completion_rate × 0.3 + world_rule_consistency × 0.3` |

## Agent: Novelist

| Aspect | Detail |
|--------|--------|
| **Purpose** | Write scene-level prose (segments) from chapter outlines |
| **Optimizes for** | Prose quality (voice consistency, vivid detail, emotional resonance), not word count |
| **Success metric** | Quality score (1-10) per segment; voice consistency across chapters |
| **Anti-pattern** | Purple prose; inconsistent voice; telling instead of showing; repetitive sentence structure |
| **Quality gate** | Minimum quality score 7.0; must advance the chapter's goal/conflict/disaster |
| **Objective function** | `avg_quality_score × 0.5 + voice_consistency × 0.3 + goal_advancement × 0.2` |

## Agent: Development Editor

| Aspect | Detail |
|--------|--------|
| **Purpose** | Review and improve segment-level prose for structure, pacing, and clarity |
| **Optimizes for** | Improvement delta (quality after vs before edit), not edit speed |
| **Success metric** | % of segments improved; average quality gain per edit pass |
| **Anti-pattern** | Over-editing (losing author voice); under-editing (missing structural issues) |
| **Quality gate** | Must improve quality score by ≥0.5; must not reduce quality |
| **Objective function** | `avg_quality_delta × 0.6 + structural_improvement × 0.4` |

## Agent: Copy Editor

| Aspect | Detail |
|--------|--------|
| **Purpose** | Final polish: grammar, punctuation, consistency, style |
| **Optimizes for** | Error detection recall (catch ALL errors), not speed |
| **Success metric** | Errors caught per 1000 words; false positive rate |
| **Anti-pattern** | Missing subtle errors; introducing new errors; changing author intent |
| **Quality gate** | Zero grammar errors in final output; style consistency across all chapters |
| **Objective function** | `error_recall × 0.7 + (1 - false_positive_rate) × 0.3` |

## Agent: Pipeline Orchestrator

| Aspect | Detail |
|--------|--------|
| **Purpose** | Coordinate all 6 agents through the generation pipeline |
| **Optimizes for** | End-to-end pipeline success rate, not individual agent speed |
| **Success metric** | % of series completed without manual intervention; total generation time; audit pass rate |
| **Anti-pattern** | Infinite retry loops; silent failures; partial generation; pushing unverified data |
| **Quality gate** | Circuit breaker: 5 consecutive failures → stop and alert; max 3 retries per segment; audit must pass after push |
| **Objective function** | `completion_rate × 0.4 + (1 / avg_time_per_segment) × 0.2 + quality_score × 0.2 + audit_pass_rate × 0.2` |

## Agent: Audit Agent

| Aspect | Detail |
|--------|--------|
| **Purpose** | Verify all Supabase state after push; dispatch fixes for missing data |
| **Optimizes for** | Detection accuracy (find every issue), not speed |
| **Success metric** | % of issues detected; % of issues auto-fixed correctly |
| **Anti-pattern** | False positives (re-pushing correct data); missing real issues; dispatching wrong fix |
| **Quality gate** | Must verify: all books exist, all chapters have content, all covers present, all summaries present |
| **Objective function** | `detection_recall × 0.4 + fix_accuracy × 0.4 + (1 / false_positive_rate) × 0.2` |
| **Fix dispatch** | `generate_covers` → missing covers; `push_series_to_supabase` → missing books/chapters; `upload_covers` → local file exists but not in Supabase; `generate_summaries` → missing synopsis/promo |
