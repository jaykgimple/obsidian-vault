# Stickman B6 "animated" render — wired into the pipeline

Status: LIVE (committed `be56825`, `cb46717`). Not yet pushed to origin.

## What got built

- `src/worker/native-anim/assemble_character.py` — builds a production cast package (`trainer`):
  chroma-key green, `fit_head` (head width 184, neck base pinned at `HEAD_BASE_LOCAL_Y=-232`),
  `fit_body` (torso to x[-72,72] × y[-258,-88]), v2 `neck_attachment` mount, 14-check `verify_binding`.
  Expressions are REAL generated art (one sprite sheet → neutral/speak/blink split), never drawn.
- `src/worker/native-anim/author.py` — content-swap bridge (script → captions, OpenRouter voice →
  audio, character → package copy, shells to the project's `run.py preflight/validate/preview`).
- `src/lib/video/stickman-render.ts` — the `visual.mode:"animated"` branch (was already present).
- Cast library committed at `cast/trainer/` (head/body/cuffs/expressions/package.json).

## What "wire it" added

- `types.ts`: `resolveVisualSource(videoModel)` + `VIDEO_MODEL_ANIMATED="stickman/b6-painted"` +
  `ANIMATED_DEFAULT_CHARACTER="trainer"`. Single source of truth for avatar/animated/faceless.
- `models.ts`: exposes `stickman/b6-painted` in the video catalog (appended always, local engine).
- Three enqueue sites (`pipeline.ts`, `/api/content/[id]/render`, `/api/generate`) now call
  `resolveVisualSource` instead of the inline `avatar vs faceless` ternary.
- `.env` (VPS, uncommitted): `STICKMAN_CAST_DIR=/root/projects/omnivoke/cast` (+ PYTHON/SKILL).
- `.env.example`: documented the three `STICKMAN_*` vars.

## How a Short routes through it

tenant `defaultVideoModel = "stickman/b6-painted"` → `resolveVisualSource` → `{mode:"animated",
characterId:"trainer"}` → `drainRenderJob` → `renderPipeline` → `renderStickman` (VPS worker) →
OpenRouter TTS → `author.py` → `run.py` → `b6_puppet` → `preview.mp4` → video path → publish.

## Verification

- `tsc --noEmit` clean; video/models tests green; `next build` succeeds.
- Real `renderPipeline` run with `visual.mode:"animated"` + `characterId:"trainer"` produced a
  720×1280 h264+aac Short (6.1s) through the `cast/trainer` package (STICKMAN_CAST_DIR resolved).

## Open / not yet done

- Not pushed to origin (local commits only).
- Only ONE cast character exists (`trainer`); adding more = new `cast/<id>/` package +
  set `defaultVideoModel` per tenant (or extend `ANIMATED_DEFAULT_CHARACTER` to read a tenant field).
- Tenant settings UI may need to surface `stickman/b6-painted` in the video-model picker.