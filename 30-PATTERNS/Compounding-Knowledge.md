---
title: Compounding Knowledge — The Core Pattern
created: 2026-06-27
tags: [pattern, compounding, architecture, meta]
status: active
aliases: [Pattern: Compounding Knowledge, The Compounding Loop]
---

# Compounding Knowledge

> Every action produces a signal. Every signal improves future actions. The loop accelerates.
> Source: → [[2026-06-26-The-Agentic-Compound-Effect]] (OctoGentic blog)
> Part of → [[00-META/Compound-Effect]]

## The Loop

```
Action → Signal → Pattern → Better Action → Better Signal → ...
```

Each cycle improves the quality of the next cycle's output. The improvement rate compounds.

## Four Compounding Metrics

| Metric | What It Measures | Where Tracked |
|--------|-----------------|---------------|
| **Learning rate** | Error reduction per cycle | → [[Pattern: Coherence-Scoring]] (fewer failures over time) |
| **Calibration drift** | Confidence accuracy trend | → [[Pattern: Self-Healing Pipelines]] (fewer false escalations) |
| **Pattern discovery rate** | New vs repeated observations | → [[30-PATTERNS/]] (new pattern notes over time) |
| **Marginal action value** | Is each action worth more than the last? | → [[Agent Objective Functions]] (improving scores) |

## The Compounding Equation

```
V(t) = V₀ × (1 + r)^t
```

At `r = 0.10` (10% improvement per cycle) and `t = 50` cycles: `V(50) = V₀ × 117.39`

## How This Vault Implements Compounding

1. **Signal capture**: Every daily note, every lesson, every pattern = one signal
2. **Signal structure**: YAML frontmatter makes signals queryable by agents
3. **Signal connection**: Wikilinks create relationships between signals
4. **Signal retrieval**: `search_files` + wikilinks = agent-accessible signal store
5. **Signal application**: Pattern notes → agent prompts → better generation

## Compounding in Practice

| Cycle | Signal | Result |
|-------|--------|--------|
| 1 | Queue desync bug | Fixed `poll_queue()` + lesson note |
| 2 | Coherence failures | Fixed threshold to 9 + story_state |
| 3 | Review save failures | Fixed service key + lesson note |
| 4 | Cover upload gap | Fixed `_generate_book_cover` + lesson note |
| 5 | Rate limit exhaustion | Created cron restart + lesson note |

Each cycle produces a lesson note. Each lesson note prevents the same failure. The vault grows. The system improves.

## The Moat

> "No single agent in this loop is irreplaceable. But the system of agents and their accumulated shared knowledge is nearly impossible to replicate from scratch."

This vault IS the moat.
