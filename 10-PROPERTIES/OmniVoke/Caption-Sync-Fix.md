---
title: OmniVoke — Caption Sync + Punctuation Fix
created: 2026-11-05
tags: [omnivoke, video, subtitles, tts, captions]
---

# Caption Sync + Punctuation Fix

Matt (partner) reviewed the last 5 produced Shorts and flagged: the burned-in
transcript is **out of sync with the voice** and has **no punctuation** (sentence
endings run together).

## Root causes (both in `src/lib/video/subtitles.ts`)

1. **Sync** — captions were char-count estimates, rescaled so the *last* word
   landed on the ffprobe-measured audio length. That anchors only the end;
   edge-tts pauses at punctuation and speaks non-uniformly, so captions drifted
   mid-video.
2. **Punctuation** — `tokenizeWords` stripped all punctuation and `chunkCues`
   rejoined stripped tokens, so every comma/period/question-mark was destroyed.

## Fix (deployed 2026-11-05)

- **Sync** — edge-tts is now invoked via `edge_tts_synth.py` with
  `boundary="WordBoundary"`, capturing real per-word offset/duration (100ns
  ticks) during synthesis. `parseWordBoundaries` → `alignWordBoundaries` maps
  them 1:1 onto script tokens; `deriveSubtitlesFromTimings` builds cues from
  real speech timing. When the spoken text diverges from the script (the
  `spokenTextForTTS` URL rewrite turns `lucentskill.com` into `lucentskill dot
  com`), alignment returns null and the pipeline degrades honestly to the
  duration-anchored estimate instead of attaching timing to the wrong words.
- **Punctuation** — `WordTiming` now carries a `startChar`/`endChar` span into
  the ORIGINAL script; `chunkCues` slices the script between the first and last
  word of each cue, so commas/periods/case survive.

## Pre-existing bugs also fixed (surfaced during testing)

- **edge-tts 403** (`WSServerHandshakeError: 403 Invalid response status`) —
  edge-tts 7.2.7 carried a stale `Sec-MS-GEC` token Microsoft revoked, breaking
  the OLD CLI path too. Upgraded the venv edge-tts to **7.3.1**.
- **QA reroll infinite loop** — `generateAndQAOneClip` declared `attempts` INSIDE
  its `for(;;)`, so a persistently-glitchy clip rerolled forever (burning
  OpenRouter credits). Moved the counter outside the loop.
- **Two stale segment-fallback tests** predating the hard-failure-retry and
  nudge-everywhere features; updated to current intended behavior.

## Verification

- 177 video tests + 726 full-suite tests green; `tsc --noEmit` clean.
- E2E smoke: real edge-tts → cues `"Hello, world! This is"` / `"the caption
  timing."` with real timing (0.10s, 2.54s, 4.35s).

## Deploy notes

- `git push` updates Vercel WEB tier only. The VPS render worker is long-lived;
  restarted it (`kill -TERM` the node child, then
  `scripts/watchdog-render-worker.sh`).
- **Open issue (separate):** worker log shows `Can't reach database server` on
  the Neon pooled endpoint (`ep-still-block-b51ajm93-pooler`). The unpooled
  LISTEN connects; the pooled drain may need a Neon-side look.
