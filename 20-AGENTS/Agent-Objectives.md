---
title: Agent Objective Functions
created: 2026-06-27
tags: [agents, objectives, reference]
status: active
aliases: [Agent Scoring, Objective Functions]
---

# Agent Objective Functions

> Every agent optimizes for something specific. These are the measurable functions.
> Owned by → [[CoS — Chief of Staff]] | Maintained by → [[CoS — Knowledge Routing]]

## Story Engine Agents

Source: → [[Story Engine — Agent Roster]]

| Agent | Objective Function | Target |
|-------|-------------------|--------|
| Architect | `continuity_score × 0.4 + chapter_completion × 0.3 + world_rule_consistency × 0.3` | Continuity alerts < 2/book |
| Novelist | `avg_quality × 0.5 + voice_consistency × 0.3 + goal_advancement × 0.2` | Quality ≥7.0/segment |
| Dev Editor | `avg_quality_delta × 0.6 + structural_improvement × 0.4` | Score ≥9/10 |
| Copy Editor | `error_recall × 0.7 + (1 - false_positive) × 0.3` | 0 grammar errors/final |
| Audit | `issue_detection × 0.5 + autofix_accuracy × 0.5` | All critical issues resolved |
| Pipeline Orchestrator | `completion_rate × 0.4 + pass_rate × 0.3 + (1/time_variance) × 0.3` | % series completing w/o manual |

## OctoGentic Agents

| Agent | Objective Function | Target |
|-------|-------------------|--------|
| Portfolio Orchestrator | `avg_property_health × 0.4 + detection_speed × 0.3 + cross_property_signal_quality × 0.3` | < 5 min detection |
| Signal Feed Generator | `avg_actionability × 0.5 + reader_engagement × 0.3 + freshness × 0.2` | Actionability ≥80% |
| Telemetry Aggregator | `anomaly_recall × 0.6 + (1 - false_alarm_rate) × 0.4` | Recall ≥ 0.95 |
| Key Takeaway Curator | `implementation_rate × 0.5 + avg_specificity × 0.3 + cross_property_applicability × 0.2` | ≥50% implemented |

## CoS (Chief of Staff)

| Metric | Target |
|--------|--------|
| Signal routing accuracy | ≥ 90% |
| Vault link health | ≥ 80% notes linked |
| Daily standup completion | 7/7 days |
| Decision routing speed | < 2 min for escalations |

---

## Compounding Effect

When agents optimize these functions:
- Errors → pattern notes (→ [[30-PATTERNS/]])
- Pattern notes → better prompts
- Better prompts → fewer errors
- Fewer errors → lower costs + higher quality

The loop compounds.
