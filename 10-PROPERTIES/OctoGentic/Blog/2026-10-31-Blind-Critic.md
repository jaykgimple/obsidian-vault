---
title: The Blind Critic
date: 2026-10-31
tags: [blog, agentic-ai, evaluation, adversarial-systems, quality-assurance, self-review]
status: published
aliases: [Blind Critic Post, 2026-10-31 Blog Post]
---

# The Blind Critic: Why Autonomous Systems Must Evaluate Their Own Output Without Knowing Who Made It

> Part of → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]] ← [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]]
> Published: 2026-10-31

## Thesis

Self-evaluation fails because the evaluator shares context with the creator. The blind critic pattern strips provenance before evaluation so judgment is based solely on the artifact and the specification.

## Key Takeaways

- **T-BC1: Strip provenance before evaluation.** Remove creator identity, design history, and rejected alternatives before the artifact reaches the critic. Blindness must be architectural, not procedural.
- **T-BC2: Evaluate against the spec, not against intent.** The specification is the only shared reference between creator and critic. Criteria bound to the spec are deterministic and auditable.
- **T-BC3: Rotate critics to prevent calibration drift.** A critic that always evaluates the same creator learns to predict rather than inspect. Rotation keeps evaluation fresh.
- **T-BC4: Detect bias through inter-critic disagreement.** When two critics evaluate the same output differently, the disagreement is a diagnostic signal. Track agreement rates and flag divergences.
- **T-BC5: Calibrate critics with seeded known-good and known-bad outputs.** Invisible calibration checks prevent criteria from drifting too loose or too tight. Refresh the calibration set regularly.

## Properties Referenced

- [[10-PROPERTIES/Darcron|Darcron]]: Gauntlet loop with provenance stripping before evaluation. Builder identity removed. Spec-bound criteria. Critic rotation. Adversarial calibration via seeded proposals.

## Related

- → [[10-PROPERTIES/OctoGentic/Blog/2026-10-16-Builder-Critic-Split|Builder-Critic Split]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-09-29-Agentic-Criticism|Agentic Criticism]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-10-23-Agentic-Taste|Agentic Taste]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-09-11-Agentic-Verification|Agentic Verification]]

## Link

Full post: `content/blog/2026-10-31-the-blind-critic-why-autonomous-systems-must-evaluate-their-own-output-without-knowing-who-made-it.md`
