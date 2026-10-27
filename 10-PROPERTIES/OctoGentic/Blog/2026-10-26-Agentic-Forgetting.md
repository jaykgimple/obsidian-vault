---
title: "Agentic Forgetting: How Autonomous Systems Know What to Unlearn"
date: 2026-10-26
tags: [agentic-ai, forgetting, decay, production-systems, state-management]
status: published
aliases: [Agentic Forgetting]
---

# Agentic Forgetting

> Part of → [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]] ← [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]]
> Published: 2026-10-26
> Word count: 1,199

## Thesis
Memory without forgetting is a liability. Forgetting is a deliberate design capability that keeps autonomous decisions accurate over time. Decay, invalidation, bounded retention, and scope-based forgetting work together to prevent stale signal dominance.

## Core Architecture
- **Decay functions**: Reduce memory weight over time unless reinforced by new evidence
- **Invalidation triggers**: Handle sudden change (role update, regime shift) immediately, not on a decay curve
- **Bounded retention with significance scoring**: Cap the memory store; prune low-significance entries; keep the pruning log auditable
- **Forgetting by scope**: Different retention rates for session, episodic, semantic, and procedural memory

## Production Example
→ [[10-PROPERTIES/Newtradium|Newtradium]] maintains a 200-pattern library with daily decay, regime-change invalidation, and significance-based pruning. Archived (not deleted) patterns can be reactivated when regimes cycle back.

## Key Takeaways
- T-AF1: Forgetting is a design capability, not a failure mode
- T-AF2: Decay for gradual drift, invalidation for sudden change
- T-AF3: Make pruning auditable
- T-AF4: Forget by scope, not globally
- T-AF5: Archive before you delete

## Related
- ← `10-PROPERTIES/OctoGentic/Blog/2026-10-17-Agentic-Memory` (Oct 17): Memory architecture, the complement to forgetting
- ← [[10-PROPERTIES/OctoGentic/Blog/2026-10-22-Agentic-Caching|Agentic Caching]] (Oct 22): Cache invalidation as a form of forgetting
- ← [[10-PROPERTIES/OctoGentic/Blog/2026-08-23-Agentic-Adaptation|Agentic Adaptation]] (Aug 23): Behavioral change through experience
- → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]]
