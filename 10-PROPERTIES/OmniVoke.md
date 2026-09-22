---
title: OmniVoke — Video/TTS Publishing
created: 2026-09-17
tags: [property, omnivoke, video, publishing]
status: active
aliases: [OmniVoke Platform, omnivoke]
---

# OmniVoke

> Multi-platform content publisher: one input (product + topic) generates the right content for every connected platform, including a generated video Short for YouTube. HITL or YOLO publish.
> Repository: `/root/projects/omnivoke` (jaykgimple/omnivoke, private) · Live: omnivoke.vercel.app · Brand: OmniVoke LLC (never "adgorithmic")
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router) + three.js 3D hero |
| Backend | Prisma 6 + PostgreSQL (Neon) |
| Auth | jose JWT |
| Deploy | Vercel (git-connected, auto-deploys on push to main) |

## Product vision

1. Connect platforms (YouTube, LinkedIn, Bluesky, X, etc.).
2. Input = a product + topic/prompt.
3. Multi-select = the CONNECTED PLATFORMS (not content types). "Hit all" = right content for every platform.
4. HITL (review each) or YOLO (publish now).

## Key Mechanisms

- **9 platforms** via `PublishAdapter` contract + registry. Adding one = 1 adapter + registration.
- **Video pipeline:** script -> TTS -> text-to-video/avatar -> ffmpeg (loop to voiceover, 9:16, ASS subtitles) -> thumbnail.
- **Queue:** Postgres `FOR UPDATE SKIP LOCKED`, no broker.
- **Attribution:** UTM + `personalization_id`, A/B variant resolution.

## Notes

- Pitfall: the picker is PLATFORMS, not content-types; no file picker for YouTube Short (it generates the short).
- OpenRouter key is per-project, often broken/drained; verify `.env` before relying on paid video gen.
- Docs rendered live at `/docs` via `remark`; edits need a redeploy.

## Multi-account publishing (2026-09-21)

Decision (Jay's "wrinkle"): one connection per platform was wrong. Now a tenant can connect **multiple labeled accounts per platform** (e.g. "LucentSkill LinkedIn" + "RoleFresh LinkedIn"), and associate each **product (Brand)** with the account(s) it publishes to. Publishing **fans out** to the brand's associated accounts per platform; each account decrypts its own token, exactly-once per account.

Shipped as a 5-piece gauntlet (builder + harsh critic, all OUR_WINS):
- P1 schema (`Integration.label`, drop `@@unique([tenantId,platform])`, `BrandAccount` junction, `Publication.integrationId` + account-scoped unique)
- P2 label at connect; P3 brand↔account association (`GET/PUT /api/brands/[id]/accounts`, tenant-scoped, `FOR UPDATE` lock); P4 publish fan-out (`resolvePublishAccounts`, account-scoped idempotency key, honest "no associated account" failure persisted as terminal run); P5 dashboard UI (grouped labeled connections + disconnect + product multi-select).

Deploy facts/lessons:
- Schema is additive-only; applied via `prisma db push --accept-data-loss` (the "data loss" warning was a false positive, 0 Publication rows). No `prisma/migrations` dir — OmniVoke syncs schema with `db push`.
- Correct Vercel projectId = `prj_xcAXFLtyRJruGySfdcKhZvKtkRm6`. `/root/.vercel/project.json` is STALE and points at **octogentic** (`prj_sKNTA...`) — trust the projects list, not the local `.vercel` link.
- Prod env (30 vars) already had Neon `DATABASE_URL` + `OPENROUTER_API_KEY` etc. populated (sensitive = redacted by API).