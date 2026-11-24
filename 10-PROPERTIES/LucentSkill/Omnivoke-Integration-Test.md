---
title: OmniVoke integration test (blog -> Short)
created: 2026-11-23
tags: [lucentskill, omnivoke, cinematic-styles, integration]
status: done
---

# LucentSkill -> OmniVoke blog pipeline

Part of -> [[LucentSkill]] · [[OmniVoke]]

## Test result (2026-11-23, brand resumed)

- Push from LucentSkill `ovk_` key -> OmniVoke `/api/v1/content` -> HTTP 201, content + render + publish jobs.
- Per-product cinematic rotation CONFIRMED live: LucentSkill brand (`cinematicStyles=[]` = all, order `random`) rendered `chalkboard` + `one-line` on two test runs (random from the 105), correctly overriding the tenant's default `kwaivgi/kling-v3.0-pro` faceless model.
- The rotation only works because `resolveCinematicVisual` (src/lib/video/cinematic-select.ts) was wired into BOTH the generate/content render routes AND `integration/pipeline.ts` (the `/api/v1/content` auto-run path the cron hits). A brand with a configured style set renders cinematic regardless of the tenant video model.

## The "ok:false" was a false alarm (root cause + fix)

The VPS crontab (`0 22 * * *` -> `run-daily-lumen.ts`) re-runs the daily blog AFTER the Vercel cron (14:00 UTC) already published, so `runDailyLumen()` returns `{published:false, skippedReason:"already published today"}` and the push was skipped. The script still logged the unset `omnivoke:{ok:false}` default -> read as a feed failure.

Fix (`ac76208`): both `scripts/run-daily-lumen.ts` and `src/app/api/cron/generate-blog/route.ts` now log `{skipped:true, reason}` on a skip instead of `ok:false`, so a real push failure is distinguishable from a deliberate no-op. The feed itself was healthy the whole time (content rows created daily at ~14:00 UTC).

## Lesson

When a daily cron has a primary (Vercel) + a backstop (VPS crontab) that both run, the backstop's "already published" skip must not log as a failure. Distinguish skip from error in the log, or every same-day re-run reads as a broken feed.