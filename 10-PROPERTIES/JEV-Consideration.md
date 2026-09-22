---
title: JEV — Consideration (revisit Sep 28, 2026)
created: 2026-09-22
tags: [property, jev, decision-model, ai-models, cross-property]
status: pending-review
aliases: [JEV Consideration, JEV-1.13]
---

# JEV (TypeSafe `jev-1.13`) — Consideration

> Cross-property evaluation of TypeSafe's "System One" decision model. Revisit week of Sep 28, 2026.
> Source: https://openrouter.ai/typesafe/jev-1.13 · Deep dive: flaviocopes.com/jev/

## What Jev is (the important correction)

NOT a faster general model. Cannot write prose, code, captions, or summaries. It is a DECISION/CLASSIFICATION primitive:

- Input: data (state) + a list of typed questions.
- Output: choices, yes/no probabilities, 0-10 scores, all with confidence.
- Price: $0.042/M input, **$0 output**. Latency ~0.24s (P50).
- ~444x cheaper + ~193x faster than an LLM on decision tasks (TypeSafe's high-end claim).
- Structurally zero type errors (returns only options you defined).
- Calibrated probabilities (RLCD training): "90% confident" is right ~90% of the time.

Three primitives: `noul` (yes/no + probability), `choice` (pick one of N, up to 255 options), `score` (2-10 level scale). Can ask 13 questions in one call (~12x cheaper than sequential).

**It reduces token consumption only by replacing LLM JUDGMENTS, not LLM GENERATION. It's a router and judge, never a writer.**

## Caveats

- Early access, waitlist (~1-2 days), released Sep 18, 2026. Unproven at scale.
- Text only, 32K context (64K state+questions), no images/audio/video.
- Bad at math/counting. Arithmetic stays in code.
- Adjunct to deepseek, never a replacement where text is generated.

## Property mapping (ranked)

1. **OmniVoke** (best fit)
   - YOLO safety net: pre-publish gate scoring "on-brand / factually grounded / right audience" before auto-publish.
   - Auto-suggest HITL reject category (wrong_audience, off_brand, low_quality, factually_wrong, too_long) + confidence.
   - Fact-fabrication check (semantic, so zod can't catch it): `noul` "does this caption invent a stat/claim not in the source?"
   - Model routing: skip the second strong-tier variant call when the master caption suffices. Biggest token-saver.

2. **Story Engine** (best cost fit)
   - Cheap coherence pre-filter BEFORE the dev_editor+novelist revision loop. Failure patterns (location teleport, contradictory info, POV shift, truncation, pronoun inconsistency) map cleanly to `noul`/`score`.
   - First pass was ~118/129 failing, so skipping revision on clean segments cuts real spend.

3. **Darcron**
   - Intake triage: bug vs feature, sensitivity tier (high/medium/yolo).
   - Cheap first-pass A/B critic verdict (generative critic still names gaps, so adjunct).

4. **LucentSkill** — free-text answer grading, content moderation, support routing.

5. **RoleFresh** (paused + DB down) — resume↔job match scoring as cheap pre-filter.

6. **Newtradium** (NOT recommended) — text-only + bad at math; signals are numeric gates. Wrong domain.

## Recommendation (pilot candidates)

Same shape for both: cheap gate in front of an existing expensive/irreversible step.

- OmniVoke YOLO pre-publish quality gate.
- Story Engine coherence pre-filter before the revision loop.

Both map onto existing scoring/review code, cut OpenRouter spend, reversible if accuracy isn't there.

## Next steps (on revisit)

- Check Jev maturity/exit-early-access + any benchmark updates.
- Spec the OmniVoke gate or Story Engine pre-filter.
- Prototype a real Jev call against real data before committing.
