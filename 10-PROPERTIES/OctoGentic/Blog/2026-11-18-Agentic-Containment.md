---
title: Agentic Containment
date: 2026-11-18
tags: [blog, agentic-ai, containment, blast-radius, fail-closed, omnivoke, darcron, safety]
status: published
aliases: [Agentic Containment Post, 2026-11-18 Blog Post]
---

# Agentic Containment: How Autonomous Systems Limit the Blast Radius of a Bad Decision

> Part of → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]] ← [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]]
> Published: 2026-11-18

## Thesis

Prevention asks whether a bad decision can be stopped before it happens. Reversal asks whether it can be undone afterward. Containment asks a different question: if the decision goes wrong, how far can it reach? The blast radius is a property of the design, not the model's accuracy: what the action may touch, how many independent gates stand between the decision and the world, and whether a human can stop the line once it moves. Containment fails three ways: the unbounded action that reaches farther than the case justifies, the shared-state cascade that travels through an unfenced dependency, and the missing kill switch that lets a failure stay in motion. The design skill is to bound the action to the case, isolate the blast radius at the seams, stage the rollout, keep an exercised kill switch, and feed every fence trip back into the design.

## Key Takeaways

- **T-CT1: Prevention asks if the bad decision can be stopped. Containment asks how far it can reach.** A system that cannot prevent every failure must be able to keep one failure from becoming ten.
- **T-CT2: Give every action the smallest reach that can do the job.** Set the reach per decision, not per system. A budget that is not written down is the maximum the system can do.
- **T-CT3: Isolate the blast radius at the seams.** Independent gates, credentials, and leases. A break in one unit must not become a break in the unit next to it.
- **T-CT4: Stage the rollout.** Let the decision meet a small, reversible surface before it meets the world, and catch the bad call while it is still cheap to be wrong.
- **T-CT5: Keep a kill switch, test it, and feed every fence trip back into the design.** A stop that is not exercised is a hope, and a fence that never trips is either perfect or invisible.

## Properties Referenced

- [[10-PROPERTIES/OmniVoke|OmniVoke]]: One input fans out to platform-native content for every account a brand owns. Containment is built into the fan-out: each account is a separate job with its own idempotency key and its own decrypted token, so one account's failure does not become the fleet's failure. Human review is a gate in front of every platform, automatic mode is a deliberate opt-in that widens the blast radius on purpose, and a missing account is a terminal run with an honest reason rather than a silent skip.
- [[10-PROPERTIES/Darcron|Darcron]]: The autonomous software factory builds its own features through a builder and a blind critic. The builder cannot contain its own work, so the fence is an independent evaluator: the change ships only when the critic picks it, a hard round limit sends an unconverged issue to needs-input instead of merging a compromise, a smoke gate runs before any pull request, and sensitivity tiers decide how much independence a change earns.

## Related

- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-17-Agentic-Recourse|Agentic Recourse]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-07-Agentic-Reversibility|Agentic Reversibility]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-15-Agentic-Invariants|Agentic Invariants]]

## Link

Full post: `content/blog/2026-11-18-agentic-containment-how-autonomous-systems-limit-the-blast-radius-of-a-bad-decision.md`
