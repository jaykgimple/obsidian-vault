---
title: Story Engine — Agent Deep-Dives
created: 2026-06-27
tags: [story-engine, agents, reference]
status: active
aliases: [Agent Details, Agent Prompts]
---

# Story Engine — Agent Deep-Dives

> Each agent's role, prompt structure, and objective function.
> Roster: → [[Story Engine — Agent Roster]]

## → [[Agent: Architect]]

| Aspect | Detail |
|--------|--------|
| **Role** | Design series structure: books, chapters, story DNA, character arcs |
| **Optimizes for** | Narrative coherence (consistent world-building, character arcs that pay off) |
| **Success metric** | Continuity alert rate < 2/book; chapter completion rate 100% |
| **Quality gate** | Every chapter must have: goal, conflict, disaster, reaction, dilemma, decision |
| **Objective** | `continuity_score × 0.4 + chapter_completion × 0.3 + world_rule_consistency × 0.3` |

## → [[Agent: Biographer]]

| Aspect | Detail |
|--------|--------|
| **Role** | Generate chapter prose drafts (~300w) from chapter outlines |
| **Optimizes for** | Efficiency (fast, consistent skeleton prose) |
| **Success metric** | Draft completion rate; minimal rejections |
| **Output** | Structured prose with goal/conflict/disaster beats |
| **Fallback** | Skeleton draft if full generation fails |

## → [[Agent: Novelist]]

| Aspect | Detail |
|--------|--------|
| **Role** | Write segment-level prose (~800w) from chapter drafts |
| **Optimizes for** | Prose quality (voice consistency, vivid detail, emotional resonance) |
| **Success metric** | Quality score ≥ 7.0; voice consistency across chapters |
| **Context** | Receives `get_story_state()` (all prior chapter summaries + last 3 segments) |
| **Revision** | Max 4 attempts; triggers on coherence < 9 |
| **Objective** | `avg_quality × 0.5 + voice_consistency × 0.3 + goal_advancement × 0.2` |

## → [[Agent: Dev Editor]]

| Aspect | Detail |
|--------|--------|
| **Role** | Review and score segments for coherence |
| **Optimizes for** | Consistency checking (location, POV, facts, character details) |
| **Success metric** | Score ≥ 9/10 to pass |
| **Dimensions** | Location (25%), POV/Tense (25%), Events (25%), Characters (15%), World (10%) |
| **Threshold** | < 9 → auto-revision trigger |
| **Objective** | `avg_quality_delta × 0.6 + structural_improvement × 0.4` |

## → [[Agent: Copy Editor]]

| Aspect | Detail |
|--------|--------|
| **Role** | Final polish: grammar, punctuation, style |
| **Optimizes for** | Error detection recall (catch ALL errors) |
| **Success metric** | 0 grammar errors in final output |
| **Objective** | `error_recall × 0.7 + (1 - false_positive) × 0.3` |

## → [[Agent: Audit]]

| Aspect | Detail |
|--------|--------|
| **Role** | Final review: duplicate titles, cover images, structural integrity |
| **Optimizes for** | Issue detection completeness |
| **Auto-fix** | Loops up to 5 times until zero critical issues |
| **Objective** | `issue_detection × 0.5 + autofix_accuracy × 0.5` |

## → [[Agent: Pipeline Orchestrator]]

| Aspect | Detail |
|--------|--------|
| **Role** | Coordinate all 6 agents through the pipeline |
| **Optimizes for** | End-to-end pipeline success rate |
| **Self-healing** | → [[Pattern: Self-Healing Pipelines]] |
| **Watchdog** | 60s health check loop |
| **Queue** | Supabase `generation_queue` + SQLite `generation_queue` |
| **Objective** | `completion_rate × 0.4 + pass_rate × 0.3 + time_consistency × 0.3` |
