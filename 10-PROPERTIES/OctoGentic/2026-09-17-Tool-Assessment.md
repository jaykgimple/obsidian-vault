---
title: Tool Assessment — Scrapling & screenshot-to-code
created: 2026-09-17
tags: [octogentic, decision, tools, infrastructure]
status: active
---

# Tool Assessment vs OctoGentic Goal (2026-09-17)

Decided against the OctoGentic thesis: cross-property signal loop, self-healing, compounding value, minimal operator overhead.

## Scrapling — ADOPTED

- Adaptive web-scraping framework, exposed as MCP server + authored a routing skill.
- Verdict: **compounding infrastructure asset.** Aligned, keep.
- Why it maps:
  - **Self-healing ingestion**: adaptive selectors auto-relocate when a source site redesigns. This is the portfolio's "resilience / self-healing" thesis made concrete. Scrapers that don't silently break = no quiet data decay.
  - **Anti-bot / stealth** lets properties pull from sources that would otherwise block (public listings, competitor reviews, metadata).
  - Serves Telemetry Aggregator ("catch subtle degradation") and Orchestrator ("detection speed") by removing a recurring silent-failure mode.
  - Implements the T-CE1 takeaway: build compounding infrastructure before features.
- Where: `/root/.venvs/scrapling`, MCP `mcp_scrapling_*` (13 tools), skill `scrapling`.

## screenshot-to-code — SKIPPED

- Human-facing web app (screenshot → React/Tailwind code). No MCP/CLI/API surface.
- Verdict: **leaf-node convenience, not a portfolio capability.** Correctly declined.
- Why it does not map:
  - One-shot artifact, no telemetry, no learning, no cross-property reuse, no compounding.
  - None of the seven portfolio properties (Story Engine, Bookbrary, RoleFresh, Darcron, OmniVoke, Newtradium, LucentSkill) have a screenshot→code need. Even the frontend-heavy ones (Newtradium, LucentSkill, Darcron) are live products with established design systems, served by the `image-to-code`/`design-taste` skills, not by a screenshot-replication app.
  - Re-humanizes a step (drag-drop UI) instead of making a property autonomous.
  - Unique bits (video→prototype, asset extraction) need new paid keys (Gemini/Replicate) with zero reuse.
- Overlap already covered in-house via the `image-to-code` skill + vision-capable delegation.
- Revisit only if video-to-prototype becomes a real property need.

## Decision Rule (for future tool evals)

Adopt only tools that (1) serve a named property or the cross-property signal loop, (2) compound (learn/self-heal/reuse), and (3) lower operator overhead. Skip tools that are single-purpose, human-facing, or add paid dependencies with no cross-property payoff.