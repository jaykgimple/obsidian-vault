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

## Recent Work
- [[10-PROPERTIES/OmniVoke/Caption-Sync-Fix]] — word-boundary caption timing + preserved punctuation (deployed 2026-11-05)
- [[10-PROPERTIES/OmniVoke/Bluesky-Connect-Fix]] — verify-on-save + credential field mismatch + handle normalization (deployed 2026-09-29)
- [[10-PROPERTIES/OmniVoke/HITL-Test-2026-09-29]] — HITL test findings: Bluesky junction fix + silent-success mask fix (deployed 2026-09-29)
- [[10-PROPERTIES/OmniVoke/HITL-Review-Redesign]] — collapsed summary + expandable rows + asset slot for multi-platform review surface (2026-09-26)

## Native-anim wiring REVERTED (2026-11-20)

Reverted the entire premature stickman native-anim integration. The earlier two gauntlets
(visual-style + native-anim) wired custom character/scene generators into the render path
before the "implement repo as-is + test it" step was confirmed. Per [[Home]] decision, that
step comes FIRST (vendor + test), then wire later.

Current clean state (deployed, commit `0596326`):
- Video engine, schema, dashboard, API restored to pre-stickman baseline (faceless/avatar intact, 731/731 tests, tsc clean, build green).
- Vendored the repo as-is and KEPT it: `src/worker/native-anim/` = 12 `b6_*.py` + `reference-b6/` assets + the passing proof `outputs/omnivoke-proof-02/preview.mp4` (298 frames, 0px contact error).
- Preserved the separate `brand-pause` kill-switch (commit `4f0946d`) on top; `Brand.paused`, PATCH `/api/brands/[id]`, dashboard Pause/Resume, publish-engine short-circuit all intact.

Key lessons (the traps that bit this session):
- **The full vendored tree was only in un-pushed local commits.** Prod (`origin/main`) had just 4 core `b6_*.py` + the custom adapters; the 8 remaining `b6_*.py` + entire `reference-b6/` + proof lived only in local commit `75c03dd` (never pushed). A `git reset --hard origin/main` silently drops them — re-checkout from the backup branch to recover.
- **Diverged histories:** prod had `brand-pause` (4f0946d) that local lacked, and local had 3 un-pushed native-anim commits prod lacked. Naive push would have wiped brand-pause. Reconcile by resetting to `origin/main` then replaying the revert on top.
- **Custom code removed (never resurrect):** native-anim-* / cast-adapters / speakers / styles / scene-background / brand-visual-style (TS) + scene_runner / character/painted/ai_painted/explainer/illustrated/minimalist adapters (Py). The authoritative workflow (run the repo as-is, content-swap only) is [[10-PROPERTIES/OmniVoke/Stickman-B6-Wiring-Plan]]; the Hermes skill `software-development/stickman-b6-engine` codifies it.

## Native rig-animation renderer (2026-11-15)

Added a second, deterministic render engine alongside the existing text-to-video path (the "Best/option 3 hybrid" from Stickman). Vendored Stickman's MIT-licensed painted-puppet rig into `src/worker/native-anim/` (b6_puppet.py etc.) on a pinned py3.12 venv (`.pyenv`), with a code-drawn character adapter (no image model, deterministic PIL/numpy sprites) and a script->scene authoring bridge. Routes by `visual.mode === "animated"` (set at enqueue when `brand.visualStyle.kind === "animated"`); faceless/avatar output stays byte-identical (regression-pinned).

Shipped as a 7-piece gauntlet, all committed to `main` (11 unpushed commits as of 2026-11-15):
- P1 vendor engine + render; P2 schema (`Brand.visualStyle` + `nativeAnimCharacter` Json) + R2 key contract; P3 code-drawn character adapter (`native-anim-character.ts` + `character_adapter.py`, SHA-256 packageVersion); P4 scene authoring (`native-anim-scene.ts` + `scene_runner.py`) -> real 720x1280 30fps mp4; P5 render integration + fail-fast guard; P6 dashboard/API selection + pending flag; P7 worker character lifecycle (pending -> generating CAS +15m lease -> ready).

Architecture invariants (the hard rules that held):
- **Python/R2 is VPS-worker-only.** `drainRenderJob` default `renderNativeAnimation` is a no-Python fallback that throws "requires the VPS worker with .pyenv and ffmpeg"; only `render-poller.ts` injects `renderNativeAnimationOnWorker` (commit 7df4a9b). Vercel `/api/render/tick` cron route must never reach Python.
- Character is code-drawn, deterministic (byte-identical across generations), no image model, no Stickman-art redistribution.
- DB: `nativeAnimCharacter` column applied via `prisma db execute` ALTER TABLE (additive jsonb), same pattern as visualStyle. No migrations dir.

Still open (not yet done): P7 closed the plumbing only; no live customer render, no git push/Vercel deploy, no worker restart. Jay deploys via git push (never manual Vercel trigger).

## Multi-character speaker-tagged cast (2026-11-15)

Layered on top of the single-character native-anim engine. A script can now drive ONE character (plain narration) or SEVERAL (speaker tags), exactly per Jay's requirement: "A. speaker tags in script; if no tags, the model decides how many characters."

Mechanism: script lines use `NAME: line` speaker tags (generation.ts instructs the model to tag multi-voice scripts and returns a `speakers: string[]` field). `parseSpeakers(script)` strips tags for TTS/subtitles while keeping cue->speaker mapping. `ensureNativeAnimCharacterCast` resolves one character PER script speaker (speaker-driven; no pre-configured cast required), and `buildNativeAnimCharacterSpec` keys character_id + seed on the speaker identity so two speakers under one brand render visually DISTINCT code-drawn characters (deterministic).

Shipped as a 6-piece gauntlet, all OUR_WINS after fixes:
- P1 speaker tags + parseSpeakers (clock-time/URL false-positive guards); P2 character LIBRARY storage (`NativeAnimCharacterLibrary {version 1, characters{}}` + `visualStyle.characters[]`); P3 style fingerprint + plural generation (regenerate only stale members); P4 multi-character scene authoring (N puppets, per-shot speaker assignment, runner installs N packages); P5 render integration (tags stripped from TTS/subtitles, speaker mapping survives); P6 speaker-driven + distinct cast (the model-decides requirement).

Key invariants held throughout:
- Single-character + faceless + avatar output is byte-identical (exact-equality regression pins).
- Python/R2 stays VPS-worker-only; the Vercel cron route throws a fallback error, never reaches Python.
- Characters are code-drawn (no image model), deterministic (same speaker+style -> same spec), with SHA-256 packageVersion + per-sprite hash verification.

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