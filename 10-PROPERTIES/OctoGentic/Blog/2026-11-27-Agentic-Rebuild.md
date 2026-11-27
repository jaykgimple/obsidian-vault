---
title: Agentic Rebuild
date: 2026-11-27
tags: [blog, agentic-ai, rebuild, story-engine, bookbrary, regeneration, consistency]
status: published
aliases: [Agentic Rebuild Post, 2026-11-27 Rebuild Blog Post]
---

# Agentic Rebuild: Why You Regenerate the Corpus, Not the Instance

> Part of → [[10-PROPERTIES/OctoGentic/Blog-Index|Blog Index]] ← [[10-PROPERTIES/OctoGentic/Overview|OctoGentic]]
> Published: 2026-11-27

## Thesis

When a generator's defect is systemic, patching it instance by instance never finishes and never matches. The Story Engine that generates books for Bookbrary stops hand-editing one flawed chapter and instead reruns the whole series through the current pipeline, so every artifact inherits every fix at once and the corpus returns to being self-consistent. Rebuild over patch is a decision with a trigger condition and a price in both directions.

## Key Takeaways

- **T-RB1: Classify the defect before choosing the tool.** Local and isolated means patch; systemic and recurring means rebuild. A flaw stamped across every artifact is one pipeline bug wearing many faces, and no number of patches reaches the cause.
- **T-RB2: The premise and pipeline are the source of truth, not the prose.** Hand-editing generated output forks the artifact away from its own generator. Rerun through the current engine and every item stays coherent with the model behind it.
- **T-RB3: The corpus is the unit of correctness when a reader consumes the whole body.** A reader compares chapter three to chapter seven, so the relationship between artifacts is what is judged. Rebuild restores the relationship; a patch only restores the part.
- **T-RB4: A rebuild must survive its own failure.** Checkpoint and resume per segment so a long regeneration can fail partway and retry only what failed, instead of corrupting the corpus it is meant to heal.

## Properties Referenced

- [[10-PROPERTIES/Story-Engine/Overview|Story Engine]]: The generation backend whose `rebuild_all` reruns a whole series through the current pipeline rather than hand-fixing the flawed chapters. The premise and pipeline are the source of truth; the prose is regenerated from them so the corpus stays coherent as a body.
- [[10-PROPERTIES/Bookbrary|Bookbrary]]: The reader that displays the corpus, and the strictest consistency checker. A reader holds chapter three and chapter seven in their head at once, so the whole series is the unit of correctness, not the book.

## Related

- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-03-Agentic-Backfill|Agentic Backfill]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-11-22-Agentic-Sequencing|Agentic Sequencing]]
- → [[10-PROPERTIES/OctoGentic/Blog/2026-10-31-Blind-Critic|Blind Critic]]

## Link

Full post: `content/blog/2026-11-27-agentic-rebuild-why-you-regenerate-the-corpus-not-the-instance.md`