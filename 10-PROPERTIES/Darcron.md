---
title: Darcron — Autonomous AI Software Factory
created: 2026-09-17
tags: [property, darcron, factory, ai-agents]
status: active
aliases: [Darcron Factory, darcron]
---

# Darcron

> Autonomous AI software factory: a Next.js control-room frontend on Vercel, a GitHub-labels state machine, and an OpenRouter build engine. Builds its own features via a builder + blind-critic gauntlet loop.
> Repository: `/root/projects/darcron` (jaykgimple/darcron, private) · Live: darcron.vercel.app
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (control-room dashboard) |
| State machine | GitHub labels (`factory:*`) |
| Build engine | OpenRouter (per-account model settings) |
| Worker | VPS systemd timer → `/api/cron` (every 15 min) |

## Key Mechanisms

- **State machine:** `factory:under-review -> planned -> in-progress -> ready-for-review -> completed` (completed = PR merged AND issue closed).
- **Gauntlet loop:** builder vs blind critic (`critic.ts` coin-flips A/B labels), ships when the critic picks ours, else `needs-input` at round 15.
- **Intake:** `/api/interview` (BRD/FRD/bug), deterministic smoke gate before PR.
- **Sensitivity tiers:** `high | medium | yolo`.
- **Model registry:** `models.ts`, `MARKUP=1.3`, live OpenRouter pricing (cached 1h); show only Darcron prices in UI.
- **Observability:** real usage ledger + live agent stream (log issue #53).

## Status

- Live. Gauntlet loop is the standard build flow (Aug 2026).
- Governance in-repo: `MISSION.md` > `FACTORY_RULES.md` > `CLAUDE.md`; read `STATE.md` on re-entry.

## Notes

- Full pitfalls, state-machine maps, and deploy procedure live in the `darcron-development` skill (not duplicated here).
- Deploy: `vercel --prod` with `VERCEL_ORG_ID` + `VERCEL_PROJECT_ID`.
- Em dashes banned in all copy; fix only via Python `\u2014` replace, not sed.