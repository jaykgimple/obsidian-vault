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
| Deploy | Vercel (NOT git-connected, manual `vercel --prod`) |

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