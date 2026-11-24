# OmniVoke Cinematic Styles (Lemo-Opuscar)

Status: 105/105 styles GAUNTLET-PASSed and WIRED. Summary below.

## What this is
Adapted lemo-opuscar's "code renders the film, no video model" engine into an OmniVoke
capability. Source cloned to /root/projects/lemo-opuscar. Research + specs live under
/root/projects/omnivoke/research/opuscar/ (MASTER_PLAN.md, INDEX.md, AUDIT_BAR.md, RUNTIME.md,
GAUNTLET.md, study/, synthesis/, styles/, new-styles/, gauntlet/).

## License decision (binding)
- core/ + tools/ = MIT (usable). styles/*/STYLE.md + DEMO.md + docs = CC BY-NC 4.0, and their
  LICENSE bans even "whole or adapted" commercial reuse. So every shipped style MUST be pure
  origination, never paraphrase. We chose pure origination (no paid licence).
- Gate: every spec needs >=3 independent non-repo sources + mechanically verified zero shared
  8-word phrases vs upstream. AUDIT_BAR.md + a Python n-gram scan are the enforcement.

## Progress
- Phase 1 (study): 5 study docs + synthesis + audit bar. DONE.
- Phase 2 (catalog): 99/99 lemo-opuscar styles adapted to original OmniVoke specs. DONE,
  reconciled (zero missing, zero overlap). stick-explainer -> our 'stick-figure'.
- Phase 3 (new): 6 brand-new styles (classical-oil-painting, anatomical-illustration,
  claymation, modern-anime, calligraphy, musical-score). DONE. Total 105 styles.
- Phase 4 (runtime): ffmpeg 7.0.2 static at /opt/ffmpeg-static (symlinks ffmpeg7/ffprobe7);
  playwright-core + chromium-headless-shell; video.mjs + mux.sh PROVEN.
- Phase 4 (gauntlet): loop PROVEN = Sonnet builder -> video.mjs render -> geometric critic
  (pixel) + gemini-2.5-flash vision judge -> precise fix -> repeat. 9/9 pilot PASS
  (stick-figure 8 rounds; the 8 Canvas styles 1 round each).
- Phase 4 (wiring): DONE. VisualSource mode "cinematic"; resolveVisualSource maps
  "opuscar/<slug>" -> cinematic; renderPipeline -> renderOpuscar (voice -> resolve film
  (pre-authored OR claude-sonnet-5.5 on-demand) -> video.mjs capture -> ffmpeg aac mux ->
  promote). VPS-only. E2E verified: real 1080x1920 h264 + aac Short. 4 hermetic unit tests.

## Decisions (Jay agreed)
- Research/spec-building: default model (deepseek). Runtime film authoring:
  anthropic/claude-sonnet-5.5 (pinned, OPUSCAR_AGENT_MODEL). Gauntlet builder/critic: Sonnet.
- Stick figure: the curve-based vector stick figure is a candidate to REPLACE the B6
  painted-puppet stickman engine (deletes the cuff/mount/hand bug class). Gauntlet-PASSed.

## Deployment notes (worker)
- renderOpuscar needs on the VPS: lemo-opuscar checkout at OPUSCAR_RUNTIME
  (/root/projects/lemo-opuscar) + ffmpeg 7 at OPUSCAR_FFMPEG_DIR (/opt/ffmpeg-static) on PATH
  + playwright chromium. Style specs + gauntlet films ship in the omnivoke repo
  (research/opuscar/), read relative to the worker cwd.
- On-demand authoring hits OpenRouter OPUSCAR_AGENT_MODEL (claude-sonnet-5.5); pre-authored
  gauntlet films (9 pilot styles) are the deterministic fallback. Other 96 styles author
  on-demand from their spec.

## Next (remaining)
- Gauntlet: COMPLETE. 105/105 styles carry a deterministic pre-authored film at
  research/opuscar/gauntlet/<slug>/index.html (renderOpuscar uses these, no LLM at render).
  Swept in 16 batches; 3 needed a fix round (map-explainer caption cutoff, microscope
  canvas-blur hang, sketchnote reveal timing).
- Optional polish (not a blocker): bundle real fonts (builders fall back to system
  serif/sans); a few styles fake WebGL/3D with 2D canvas (fine on the no-GPU VPS).

## Pitfalls learned
- deepseek spec agents intermittently COPY upstream prose; kimi was clean but exhausted credits
  (delegation.model switched to deepseek mid-sweep, then Sonnet for the gauntlet). Every batch
  must be n-gram audited + offenders re-dispatched with a baked-in self-check. Child
  self-reports of "0 overlap" are NOT reliable.
- delegate_task children share nothing: dropped context produced broken batches (recurring;
  treat a goal-only/context-less task as a hard defect, stop + re-dispatch).
- Subagent children have NO vision tool (deepseek AND Sonnet). Use OpenRouter
  google/gemini-2.5-flash with base64 frames for the aesthetic judge. A geometric critic alone
  grades geometry correct while a vision model reads the same pose wrong (point vs present).
- Filmcraft: a limb must end in EMPTY AIR aimed AT the prop (>=90px) to read as a point;
  landing on/near the prop reads as holding. Props must be grounded or they read as floating.
- Keep batches <=6 (OpenRouter in-flight 402 credit cap).