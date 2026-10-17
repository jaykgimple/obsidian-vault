# Daily Lumen — Reliability Fix (cron timeouts)

Date: 2026-10-06

## Problem

The Daily Lumen blog intermittently skipped days (2026-09-22, 2026-10-03, 2026-10-05).
Root cause: the daily generation (16 parallel feeds, ~8s poll, then an 1100-1300 word
Prism LLM call with NO timeout) occasionally exceeds Vercel's serverless function limit,
so Vercel kills the run mid-generation and that day publishes nothing.

## Fix

Added a reliable on-VPS trigger as a daily catch-up:

- `scripts/run-daily-lumen.ts` calls `runDailyLumen()` directly (bypasses the Vercel
  HTTP route + CRON_SECRET layer; no serverless timeout).
- System crontab: `0 22 * * *` (22:00 CEST = 20:00 UTC, AFTER Vercel's 14:00 UTC cron),
  with a `timeout 3600` guard, logging to `logs/daily-lumen.log`.
- Idempotent: the per-day guard + advisory lock make a same-day re-run (Vercel cron +
  crontab both firing) a safe no-op, so one publishes and the other skips.

## Gap / follow-up

Resolved 2026-10-06: added `OMNIVOKE_API_KEY` to `.env.local` and wired the VPS
runner to push each published post to OmniVoke (matches the Vercel route). The
three skipped days were backfilled (09-22, 10-03, 10-05) with an OmniVoke push
each.

Still open (optional): the VPS runner does not send the subscriber digest EMAIL
on catch-up days, because the Resend key is not in `.env.local`. To close that,
either add the Resend key and run the full route logic from the crontab, or add
a timeout to the Prism LLM call so Vercel fails fast instead of timing out.