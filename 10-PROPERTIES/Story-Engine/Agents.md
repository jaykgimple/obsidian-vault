---
title: Story Engine — Agent Roster
created: 2026-06-27
tags: [story-engine, agents, reference]
status: active
---

# Story Engine — Agent Roster

All agents owned by → [[Story Engine — Overview]]

| Agent | Model/Path | Role | Self-Healing |
|-------|-----------|------|--------------|
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Architect|Agent: Architect]] | `openrouter/owl-alpha` | Series outline, story DNA, character arcs | Auto-retry on 429 |
| → [[Agents|Agent: Biographer]] | `openrouter/owl-alpha` | Chapter prose drafts (300w) | Skeleton fallback |
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Novelist|Agent: Novelist]] | `openrouter/owl-alpha` | Segment prose (~800w) | Revision loop (max 4) |
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Development Editor|Agent: Dev Editor]] | `meta-llama/llama-3.2-3b` | Consistency scoring (≥9) | Auto-fail triggers revision |
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Copy Editor|Agent: Copy Editor]] | `openrouter/owl-alpha` | Grammar, punctuation, style | PASS/FAIL gate |
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Audit Agent|Agent: Audit]] | `openrouter/owl-alpha` | Final review, duplicate titles, cover | Auto-fix loop (max 5) |
| → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Pipeline Orchestrator|Agent: Pipeline Orchestrator]] | `openrouter/owl-alpha` | Coordinates all 6 agents | → [[Self-Healing-Pipelines]] |

## Generation Stats (2026-06)
- The Chrono-Compass Chronicles: 156 segments, ~51K words
- The Last Ural Owl: 52 segments, ~27K words
- Red Genesis: 3 books, ~60K words (in progress)
- Algetasadoria: 220 segments, ~97K words

## Infrastructure
- → [[Agent-Details]] — per-agent deep-dives
- → [[Pipeline|Story-Engine Queue Worker]]
- → [[Story-Engine — Watchdog]]
- → [[Story-Engine — Review System]]
