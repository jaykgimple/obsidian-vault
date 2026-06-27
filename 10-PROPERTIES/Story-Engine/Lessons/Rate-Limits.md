---
title: Lesson: Rate Limit Management
created: 2026-06-27
tags: [lesson, ops, infrastructure]
status: active
---

# Lesson: Rate Limit Management

> Daily quota: 1000 LLM requests. Exhaustion causes silent failures, not errors.

## What Happened
- Full book generation burns ~1000+ requests
- Run-all process silently stops when 429 hits
- Circuit breaker doesn't distinguish rate limits from errors
- Result: Partial generation, unpushed data

## Architecture Fix
- CoS monitors quota usage (estimate: 20 requests/segment × 52 segments = ~1040)
- Pre-check quota before starting new series
- Schedule large jobs after reset (02:00 CEST)
- Cron `resume-red-genesis` at 02:30 ensures fresh quota

## Key Metric
| Agent | Requests/Series | % of Daily Quota |
|-------|---------------|-------------------|
| Story Engine (1 book, 52 seg) | ~1040 | 104% |
| Review (per chapter) | ~2-4 | 0.2-0.4% |

**Implication**: One full book generation consumes the ENTIRE daily quota. Review must run on a different day.
