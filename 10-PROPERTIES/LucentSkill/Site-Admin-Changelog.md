---
title: Site Admin Changelog
created: 2026-11-20
tags: [lucentskill, changelog, site-admin, feature]
status: live
---

Part of → [[LucentSkill]]

# Site Admin Changelog (LucentSkill)

A plain-language release-notes log, live in site admin at `/site-admin/changelog`.

## Goals (Jay's ask)

- Changelog page in site admin, readable by a GENERAL audience (not technical).
- Backfilled with the full build history.
- Every future build auto-gets an entry.

## How it works

- **Storage**: `changelog_entries` table (migration 046). `dedupe_key` is unique: the git commit SHA for auto-ingested deploys, or a stable slug for curated history. `src/lib/changelog.ts` = data layer (`upsertChangelog` by key, `listChangelog`, `updateChangelog`).
- **Backfill** (25+ curated entries, plain English): `scripts/changelog-backfill.ts`, idempotent. Run via `node --env-file=.env.local --import tsx scripts/changelog-backfill.ts`.
- **Future builds (automatic)**: Vercel `deployment.succeeded` webhook → `/api/webhooks/vercel/changelog`. HMAC-signed; secret `VERCEL_WEBHOOK_SECRET` in Vercel env == `pass show lucentskill/vercel-webhook-secret`. Inserts an entry keyed by commit SHA, stripping the `type(scope):` prefix. Webhook id `account_hook_8f1XOHgNur8sT2fpcwlfKQOh`.
- **Tone**: the webhook guarantees coverage but inserts the technical commit message. To keep wording general-audience, reword the auto-entry for each build (same SHA → upsert overwrites). Admin console has Add/Edit (MFA-gated, audited) at `/api/site-admin/changelog`.

## Notes

- Event type is `deployment.succeeded` (NOT `deployment.ready`, which Vercel rejects for project-scoped hooks; API also rejects a `secret` body field and `events` must be strings).
- Vercel env changes need a redeploy to take effect (used an empty commit).
