---
title: CoS — Knowledge Routing
created: 2026-06-27
tags: [cos, delegation, routing]
status: active
aliases: [Delegation Map, Agent Routing]
---

# CoS — Knowledge Routing

> How the Chief of Staff routes signals between agents and properties.
> Part of → [[CoS — Chief of Staff]]

## Routing Rules

| Signal Type | Route To | Action |
|-------------|----------|--------|
| Story Engine failure | → [[Pattern: Self-Healing Pipelines]] | Auto-recover via watchdog |
| Coherence failure (<9) | → [[Pattern: Coherence-Scoring]] | Trigger novelist revision |
| Rate limit exhaustion | → [[Lesson: Rate Limit Management]] | Stop all, schedule restart |
| New takeaway discovered | → [[10-PROPERTIES/OctoGentic/Key-Takeaways]] | Add note, link to source |
| Cross-property insight | → [[30-PATTERNS/Compounding-Knowledge]] | Create pattern note |
| Daily standup | → [[40-LOGS/]] + [[00-META/Home]] | Update dashboard |
| User escalation | → [[CoS — Chief of Staff]] | Evaluate, route, resolve |

## Model Routing (Local Multi-Model)

| Model | Role | Primary Triggers |
|-------|------|-----------------|
| `openrouter/owl-alpha` | Daily Speed Driver | Default, formatting, planning, syncs |
| `qwen/qwen3-coder:free` | Software Engineer | Code, schemas, migrations |
| `openrouter/owl-alpha` | Analytical Thinker | Multi-file bugs, structural design |
| `meta-llama/lla-3.2-3b-instruct:free` | Background Compression | Context window management |

## Vault Maintenance

| Task | Frequency | Trigger |
|------|-----------|---------|
| Daily note creation | Daily | Every standup |
| Orphan scan | Weekly | No inbound links > 30 days |
| Link health check | Weekly | Broken wikilinks |
| Compounding metrics | Daily | Count notes, links, cross-refs |
| Pattern extraction | Per event | New failure/recovery → pattern note |

## Decision Routing

| Decision Type | Route |
|---------------|-------|
| Affects core goals | Escalate to principal |
| Affects organizational structure | Escalate + present options |
| Housekeeping/syntax | Handle & brief at next sync |
| Nice-to-have/no deadline | Park in deferred section |
