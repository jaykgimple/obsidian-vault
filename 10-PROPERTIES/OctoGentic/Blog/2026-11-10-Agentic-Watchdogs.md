---
title: Agentic Watchdogs
date: 2026-11-10
tags: [blog, agentic-ai, watchdogs, liveness, health, reliability, omnivoke, story-engine, bookbrary, operations]
status: published
aliases: [Agentic Watchdogs Post, 2026-11-10 Blog Post]
---

# Agentic Watchdogs: Why Liveness Is Not Health

> Part of → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]] ← [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]]
> Published: 2026-11-10

## Thesis

Health is proven progress, not existence. A watchdog that checks only liveness will watch a frozen worker burn, because a stuck process and a working process look identical to a liveness probe. The design skill is to monitor the work product (freshness, state transitions, evidence-carrying heartbeats), put the watchdog itself on a dead man's switch, and make detection carry a recovery path with bounded restarts and escalation.

## Key Takeaways

- **T-WD1: Check progress, not presence.** Liveness proves a process exists. Freshness, transitions, and output prove work is happening. Monitor the work product, not the process table.
- **T-WD2: Treat a silent log as an alarm.** A log that has not moved is not quiet, it is stuck. Freshness is the cheapest external progress signal.
- **T-WD3: Put a clock on every state.** A task that stays in the same state past its dwell limit is sick even while its process is perfect. Health is measured by transitions.
- **T-WD4: Make the heartbeat carry evidence.** A heartbeat that reports what the worker last completed can be verified by a third party. A heartbeat that only says "I am here" is liveness in disguise.
- **T-WD5: Monitor the monitor.** A watchdog that can fail silently is a single point of failure. Use a dead man's switch, and make detection carry a recovery path and an escalation.

## Properties Referenced

- [[10-PROPERTIES/OmniVoke|OmniVoke]]: The render worker froze in a database error loop overnight while the process stayed up and the watchdog stayed green, because the watchdog only checked liveness. The fix is a health check with teeth: log freshness, a database heartbeat, and queue drain rate. Alive-but-stuck workers now restart automatically and the restart is recorded as an event.
- [[10-PROPERTIES/Story-Engine/Overview|Story Engine]]: The generation backend behind [[10-PROPERTIES/Bookbrary|Bookbrary]] tracks each segment through defined states, but queue rows once sat in a generating state long past any reasonable dwell time. A restart loop alone does not prove health; a state machine needs a per-state clock, and the watchdog must check the clock, not just the process.

## Related

- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-09-Agentic-Slack|Agentic Slack]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-08-Agentic-Termination|Agentic Termination]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-06-Agentic-Escalation|Agentic Escalation]]

## Link

Full post: `content/blog/2026-11-10-agentic-watchdogs-why-liveness-is-not-health.md`
