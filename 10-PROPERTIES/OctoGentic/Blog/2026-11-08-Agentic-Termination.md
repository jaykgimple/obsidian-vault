---
title: Agentic Termination
date: 2026-11-08
tags: [blog, agentic-ai, termination, completion, rolefresh, story-engine, bookbrary, darcron, quality]
status: published
aliases: [Agentic Termination Post, 2026-11-08 Blog Post]
---

# Agentic Termination: How Autonomous Systems Know When the Work Is Done

> Part of → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]] ← [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]]
> Published: 2026-11-08

## Thesis

Termination is a designed finish line, not the absence of effort. Starting has a clear trigger: a request arrives, a task appears, a goal is set. Ending does not. Agents fail at stopping in three ways: they mistake tool success for outcome success, score thresholds for quality, and done for perfect. The design skill is to write a completion contract before the work begins, define the evidence that proves the outcome, separate completion from perfection, and give the miss path as much design as the success path.

## Key Takeaways

- **T-TM1: Write the finish line before the work begins.** A completion contract defines what done looks like, what evidence proves it, and what is out of scope. Without it, the agent stops at the first plausible signal.
- **T-TM2: Terminate on outcome evidence, not tool success.** A success code proves a step ran. It does not prove the outcome exists. Verify the result the consumer will see.
- **T-TM3: Never terminate on a score alone.** Scores are proxies and can be gamed, flat, or tied by genuinely better work. Use failure shapes and explicit criteria as the gate.
- **T-TM4: Separate completion from perfection.** Completion is the state where the output meets the requirements and is safe to hand over. Perfection is unbounded and cannot be a stopping condition.
- **T-TM5: Give the miss path as much design as the success path.** When the finish line is not reached, escalate, degrade, or stop and report. A system with a finish line and no miss path drifts.

## Properties Referenced

- [[10-PROPERTIES/RoleFresh|RoleFresh]]: The resume rewrite pipeline is prompt-first and fail-open. It does not stop because a score is low; it stops only on fabrication-shaped failures (empty output, a verbatim echo of the original, dropped lines). The human accept/redo decision is the only place the work is declared done.
- [[10-PROPERTIES/Story-Engine/Overview|Story Engine]]: Writes a book as many segments. The orchestrator tracks progress through defined states, bounds each segment with retries, and trips a circuit breaker after consecutive failures. A stop is a first-class outcome, not a crash.
- [[10-PROPERTIES/Bookbrary|Bookbrary]]: Holds the real finish line: whether the page renders. The pipeline once finished cleanly and the queue reported success while the reader displayed books with zero words, because the content had never been aggregated and pushed. The generation side had terminated on its own success signal; the reader refused to.
- [[10-PROPERTIES/Darcron|Darcron]]: Runs a builder and blind-critic gauntlet loop. The termination rule is a round limit: when the critic has not converged after fifteen rounds, the factory moves the issue to a state called needs-input and stops. Termination as a handoff, not a failure.

## Related

- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-07-Agentic-Reversibility|Agentic Reversibility]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-06-Agentic-Escalation|Agentic Escalation]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-05-Agentic-Consent|Agentic Consent]]

## Link

Full post: `content/blog/2026-11-08-agentic-termination-how-autonomous-systems-know-when-the-work-is-done.md`
