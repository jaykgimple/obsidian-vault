---
title: OctoGentic — Agentic Objectives
created: 2026-06-27
tags: [octogentic, agents, objectives]
status: active
aliases: [OctoGentic Agent Objectives, Portfolio Agent Scoring]
---

# OctoGentic — Agentic Objectives

> Source: `octogentic/AGENTIC_OBJECTIVES.md`
> Part of → [[10-PROPERTIES/OctoGentic/Overview]]
> Related: → [[Agent Objective Functions]], → [[OctoGentic — Portfolio Overview]]

## Agent: Portfolio Orchestrator

| Aspect | Detail |
|--------|--------|
| **Purpose** | Coordinate all properties in the OctoGentic portfolio |
| **Optimizes for** | Portfolio-wide agent health and cross-property intelligence sharing |
| **Success metric** | % of properties reporting healthy telemetry; time-to-detect issues |
| **Anti-pattern** | Single property failure cascading to portfolio; blind spots in monitoring |
| **Objective function** | `avg_property_health × 0.4 + detection_speed × 0.3 + cross_property_signal_quality × 0.3` |

## Agent: Signal Feed Generator

| Aspect | Detail |
|--------|--------|
| **Purpose** | Publish daily blog content (OctoGentic Signal Feed) |
| **Optimizes for** | Content quality and relevance, not publish frequency |
| **Success metric** | Reader engagement; takeaway implementation rate |
| **Anti-pattern** | Publishing for the sake of publishing; low-signal content |
| **Objective function** | `avg_takeaway_actionability_score × 0.5 + reader_engagement × 0.3 + content_freshness × 0.2` |

## Agent: Telemetry Aggregator

| Aspect | Detail |
|--------|--------|
| **Purpose** | Collect and analyze health telemetry from all properties |
| **Optimizes for** | Anomaly detection recall (catch all real issues), not precision |
| **Success metric** | Time-to-detect property health degradation; false alarm rate |
| **Anti-pattern** | Alert fatigue from noisy signals; missing subtle degradation |
| **Objective function** | `anomaly_recall × 0.6 + (1 - false_alarm_rate) × 0.4` |

## Agent: Key Takeaway Curator

| Aspect | Detail |
|--------|--------|
| **Purpose** | Extract actionable takeaways from blog posts and track implementation |
| **Optimizes for** | Takeaway actionability (can it be implemented?), not quantity |
| **Success metric** | % of takeaways marked as implemented; time from takeaway to implementation |
| **Anti-pattern** | Vague takeaways that can't be acted on; takeaways that duplicate existing features |
| **Objective function** | `implementation_rate × 0.5 + avg_takeaway_specificity × 0.3 + cross_property_applicability × 0.2` |

---

## Cross-Property Compounding

These objectives feed the vault's compounding loop:
- Signal Feed takeaways → [[10-PROPERTIES/OctoGentic/Key-Takeaways]] → inform Story Engine prompts
- Telemetry signals → [[40-LOGS/]] daily notes → inform CoS decisions
- Portfolio health → [[00-META/Home]] dashboard → visible to all agents
