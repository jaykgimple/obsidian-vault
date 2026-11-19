---
title: OmniVoke Brand-Level Pause (LucentSkill paused)
created: 2026-11-18
tags: [omnivoke, lucentskill, brand, pause, feature]
status: resolved
---

# Brand-level pause in OmniVoke

Part of → [[OmniVoke]] · [[LucentSkill]]

## What happened

Jay wanted the LucentSkill product "paused" so its auto-generated Shorts stop going out. The first approach (removing the blog cron) was rejected: it broke the daily blog mechanic instead of pausing the product. The correct fix is a **brand-level pause in OmniVoke**: a `paused` flag on the product that stops PUBLISHING while leaving the feed (blog -> OmniVoke push) mechanically intact.

## What shipped (deployed 2026-11-19)

- **`Brand.paused` (Boolean, default false)** — additive `prisma db push` (no migrations dir).
- **Publish engine gate** (`publishContentToPlatforms`): a paused brand short-circuits the fan-out -> `{ paused: true, runs: [] }`. No Publication rows, no provider call, no state transition. Single choke point for worker / manual / approval / scheduler / recycle paths.
- **Worker** (`drainOne`): settles a paused no-op job CANCELLED (no recycle, no "published" webhook).
- **`/api/publish`**: honest 409 "This product is paused".
- **`/api/v1/content`**: paused brand still creates DRAFT but skips the auto-run (no wasted video render); response carries `paused: true`.
- **`PATCH /api/brands/[id]`** + dashboard **Pause/Resume** toggle + "Paused" pill.
- **LucentSkill brand set `paused = true`** in prod.
- **LucentSkill blog cron restored** (`vercel.json` `generate-blog` + VPS `run-daily-lumen` crontab) — the daily blog keeps publishing on lucentskill.com; only the OmniVoke Short/social fan-out is paused.

## Result

Daily at 14:00 UTC the blog still generates + publishes on lucentskill.com and pushes to OmniVoke, but OmniVoke creates a DRAFT and publishes nothing. No Shorts go out until the LucentSkill brand is resumed (dashboard toggle or `PATCH /api/brands/[id]`).

## ⚠️ Git state caveat (OmniVoke)

OmniVoke `main` is **diverged**: local `main` has 3 UNPUSHED native-anim commits (75c03dd, 47c83fc, 60e2766) that are NOT deployed; origin/main got only the pause commit (4f0946d) on top of c3a6ff7. The pause was deployed on a clean branch from origin/main so Jay's in-flight native-anim work was left untouched (local `main` = "ahead 3, behind 1").

**`60e2766` is broken**: it deleted `native-anim-character-worker.ts` (plus the custom character-cast train — `native-anim-character.ts`, `native-anim-scene.ts`, adapters, etc.) but left `worker-db.ts` importing `ensureNativeAnimCharacterCast` from it — so local `main` HEAD does not build and 6 test files fail. The native-anim render path (`native-anim-render.ts`) still references the removed cast in its guards, so this refactor is mid-migration, not deployable as-is. Left untouched for Jay to finish. To resume: `git pull --rebase` replays the 3 WIP commits onto origin/main, then finish wiring the b6_puppet/run.py replacement in `worker-db.ts`.

## Lesson

"Pause a product" belongs as a flag on the product (kill-switch in the publish engine), not by deleting the upstream cron that feeds it — the cron is a working mechanic; removing it breaks the pipeline instead of pausing its output.
