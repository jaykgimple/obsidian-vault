---
title: Agentic Criticism
date: 2026-09-29
tags: [blog, agentic-ai, criticism, quality, adversarial, production-systems]
status: published
aliases: [Agentic Criticism: How Autonomous Systems Evaluate Quality Without Skin in the Game]
---

# Agentic Criticism: How Autonomous Systems Evaluate Quality Without Skin in the Game

> Blog post for 2026-09-29. Published to Signal Feed.

## Metadata

- **Slug**: 2026-09-29-agentic-criticism-how-autonomous-systems-evaluate-quality-without-skin-in-the-game
- **Word count**: 1,153
- **Reading time**: ~5 min
- **Position**: Post #99 in Signal Feed

## Key Takeaways

- **T-CR1: Separate the Evaluator From the Producer.** The agent that created the output is structurally incapable of evaluating it honestly. Use a separate evaluation process that reasons from the output alone, without access to the producer's intent or self-assessment.
- **T-CR2: Anchor Scoring to External Standards.** A rubric that drifts toward whatever the system typically produces produces scores that rise while absolute quality stays flat. Recalibrate against ground truth at regular intervals.
- **T-CR3: Make Criticism Adversarial and Blind.** The strongest evaluation comes from an incentivized critic that does not know which output is the system's. Blindness removes the bias that knowledge of origin introduces.
- **T-CR4: Calibrate the Rubric to Long-Term Quality.** A feature that works today but creates coupling that breaks tomorrow is not good. Encode maintainability, readability, and architectural fit into the scoring weights.
- **T-CR5: Bound Iteration and Escalate Persistent Disagreement.** A system that iterates forever on the same work is not improving, it is stuck. Define a round budget, and when the budget is exhausted, escalate to human judgment rather than shipping by default.

## Summary

A system that evaluates its own output is a system grading its own homework. Criticism is the capability that breaks the conflict of interest. Three failure modes: self-assessment bias, criterion drift, blind spot recursion. Three subsystems: independent evaluation, calibrated scoring, adversarial structure. Grounded in Darcron's blind-critic gauntlet loop.

## Related

- → [[10-PROPERTIES/Darcron|Darcron]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-09-25-Agentic-Coherence|Agentic Coherence]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-09-11-Agentic-Verification|Agentic Verification]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-09-27-Agentic-Degradation|Agentic Degradation]]
- → [[10-PROPERTIES/OctoGentic/Key-Takeaways|Key Takeaways]]
