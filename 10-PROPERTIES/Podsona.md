# Podsona

Video-podcast generator: clone a host, one prompt -> scripted / voiced /
lip-synced episode. Repo: `/root/projects/podsona`. Site: podsona.vercel.app.

## Current state (working CPU pipeline)

End-to-end pipeline runs on the VPS (12 CPU, NO GPU). All 8 stages implemented
and verified with a real episode (script -> ... -> provenanced -> RSS published).

- **Worker**: long-lived BullMQ worker, `npm run worker` (= `tsx --env-file=.env
  src/worker/index.ts`), kept alive by `scripts/watchdog-worker.sh` under a
  `*/5` cron.
- **Queue**: BullMQ + local Redis (`redis://localhost:6379`), one queue per
  stage (`podsona-<stage>`).
- **DB**: Neon Postgres (Prisma schema in `prisma/schema.prisma`), already
  pushed. Own Neon project (ep-frosty-sky-...).
- **Storage**: Cloudflare R2 via `@aws-sdk/client-s3`, bucket `podsona-media`
  (separate from omnivoke-media). Keys namespaced `episodes/<id>/...`.
  ⚠️ Previously misconfigured to `omnivoke-media` (mixed projects); ~253
  Podsona objects still sit in that bucket pending a cleanup move.
- **Public serving**: Vercel `/media/[...key]` route streams R2 objects.

### Stage -> CPU impl (GPU upgrade stays behind the same seam)

| stage | now | later |
|---|---|---|
| script | OpenRouter deepseek (JSON turns) | same |
| voice | edge-tts (word-timed VTT) | GPT-SoVITS/CosyVoice LoRA / ElevenLabs |
| identity | deterministic host-card PNG (initials+gradient) | FLUX LoRA + PuLID + ArcFace |
| lipsync | ffmpeg showwaves (audio-reactive) | MuseTalk / LivePortrait |
| captions | merge per-turn VTT (offset) | whisperX |
| assemble | ffmpeg H.264 + AAC + burned subs | same |
| provenance | sha256 + HMAC content manifest | C2PA + AudioSeal |
| publish | Podcasting 2.0 RSS (YouTube best-effort) | same |

### Publish is MANUAL (Jay's call)

DAG stops at `provenanced` (preview-ready). Publish only fires from the Studio
Publish button (`/api/episodes/[id]/publish`), or a download. `orchestrate.ts`
`NEXT["provenance"] = null`.

## Enqueue -> VPS (LIVE, end-to-end)

Vercel cannot reach the VPS's localhost Redis, so the pipeline uses a Neon
LISTEN/NOTIFY bridge (mirrors OmniVoke's render-poller):

- `enqueueJob` writes the Job row to Neon (persisting `payload`) and fires
  `pg_notify(podsona_jobs, id)` via Prisma `$queryRaw` — a single statement, so
  it works from Vercel's pooled connection. It never touches Redis.
- The VPS worker runs `src/worker/bridge.ts`, which `LISTEN`s the channel on a
  session-mode `DATABASE_URL_UNPOOLED` connection and drains `queued && !dispatched`
  Job rows into the local BullMQ queues (single enqueue path for both origins).
- Wake sources: pg_notify (instant), listener reconnect (recovers notifies lost
  during Neon autosuspend), and an exponential-backoff sweep (base 20s -> 10 min;
  the cap exceeds Neon's ~300s autosuspend so the compute suspends when idle).

## Key decisions

- **CPU-first, GPU-extensible**: kept `VoiceProvider` factory, `IdentityAsset.
  modelBase`, stage seams so GPU swaps in later without reworking orchestration.
- **Linear DAG for now**: `FANOUT_STAGES` / `FANIN_STAGES` emptied (per-speaker
  parallelism deferred to GPU renderers). Correctness over parallel first.
- **Storage abstraction** `src/lib/storage.ts`: R2 backend, exact keys (no
  hidden prefix), `/media` proxy for public URLs.
- **Manual publish** (see above).
- **Enqueue via Neon LISTEN/NOTIFY bridge** (solved): Vercel writes the Job row
  + fires `pg_notify`; the VPS bridge LISTENs + drains into local BullMQ. No
  Redis reachable from Vercel needed. See "Enqueue -> VPS" above.

## Lessons / gotchas

- **Watchdog env loading**: `env $(grep ...) cmd` mangles DATABASE_URL (Prisma
  throws "URL must start with postgresql://"). Use `tsx --env-file=.env`.
- **ffmpeg -shortest drops the audio stream** when the frame is a non-looping
  still. Use `-loop 1 -i frame.png` + explicit `-t <dur>` (not -shortest).
- **Sibling `.env.local` OPENROUTER_API_KEY can be a placeholder** (darcron has
  `your_openrouter_api_key`). Real key lives in lucentskill/.env.local.
- Prisma `Job` model has no `createdAt` (only startedAt/finishedAt). e2e/verify
  scripts must order by id/startedAt.
- `@aws-sdk/client-s3` must be in package.json (was only a transitive in
  node_modules).
- **Hallo2 face/voice must MATCH**: the demo ships a woman image + man audio
  (mismatched). Generate the FLUX portrait to match the character's assigned
  voice (same gender/appearance), square 512x512, face 50-70%, front-facing.

## Env (see .env.example)

DATABASE_URL, REDIS_URL, OPENROUTER_API_KEY, R2_ENDPOINT/ACCESS_KEY_ID/
SECRET_ACCESS_KEY/BUCKET_NAME, PODSONA_SIGNING_SECRET, PUBLIC_MEDIA_BASE,
FEED_BASE_URL. R2 creds also set on Vercel (for /media route).

## GPU talking-head (Hallo2 on Modal) — 2026-10-04

Decision: the talking-head stage is genuinely GPU-bound (no practical CPU path;
every self-hostable model is CUDA-first and already slower-than-realtime on a
GPU). Identity still (FLUX portrait) stays CPU/OpenRouter; the motion graduates
to GPU. GPU host = **Modal** (serverless, scale-to-zero, $30 free credits).

- **Modal workspace**: `billing-95875`. Token in `/root/.modal.toml` on the VPS
  (via `modal setup` login-link flow). CLI = `uv tool install modal`.
- **Model = Hallo2** (fudan-generative-vision/hallo2, MIT core): audio-driven
  portrait animation, still image + WAV -> continuous long-duration video
  (showcase runs 18-23 min up to 1 hr). NO pose sequence (motion comes from the
  audio via wav2vec + AnimateDiff). Chosen over EchoMimicV2, which needs a
  ~14s pose clip (`.npy` DWPose keypoints) and can't do continuous episodes.
- **Deployment**: `/root/projects/podsona/modal/hallo2.py`. CUDA 11.8 +
  torch 2.2.2 cu118 (the repo's tested env), A100-40GB. Weights (~12GB) in a
  Modal Volume (`podsona-hallo2-weights`), one `huggingface-cli download`.
- **Hallo2 contract**: source image (square 512x512, face 50-70%, front-facing)
  + WAV audio -> `scripts/inference_long.py` -> merged `merge_video.mp4`
  (512x512, then upscale for 1080p; the bundled 4K SR is CodeFormer/S-Lab,
  non-commercial, so upscaling uses a permissive upscaler).
- **Output**: 512x512 base (SD1.5). No published RTF; budget A100-40GB ~$2.50/hr
  and diffusion-scale (multi-minute episodes = tens of minutes of GPU).
- **AI-human vs clone**: both run FLUX (or the person's photo) -> Hallo2.
  Clone also needs a signed likeness/voice release + EU AI Act Art.50 synthetic
  label. Full detail in `podcast-studio/research/rounds/R02` + `R09`.

## EchoMimicV3 pivot (2026-10-04)

- **Hallo2 superseded.** Hallo2 renders a tight head-and-shoulders; compositing
  it produced "floating heads pasted on a background", which Jay rejected. The
  character must be a person IN the scene (half-body behind desk / full body on
  couch).
- **Model = EchoMimicV3** (antgroup/echomimic_v3, AAAI 2026, 1.3B, Alipay),
  built on Wan2.1-Fun-1.3B-InP. "Talking body" mode animates head + torso +
  arms + hands. Takes a TEXT PROMPT specifying framing/posture/gestures/
  background (guidance_scale 3-6 = prompt-following) + multi-aspect output
  (aspect follows the reference image dims).
- **Framing knob** (`framing: "desk" | "couch"` per character/show) maps to:
  1. FLUX reference (half-body behind desk vs full body on couch)
  2. V3 text prompt (seated waist-up vs full-body seated)
  3. aspect ratio (via the reference image dims)
- **Honest bound**: V3 animates the body but NOT the legs. True full-body leg
  animation is still unreleased (OmniHuman-1 has no public weights). For a
  seated "couch" shot the legs stay still, which reads naturally. Face is
  smaller in full-body framing -> weaker lip sync than half-body.
- **Inputs**: reference RGB + face mask (retinaface detect) + WAV audio + text
  prompt. Audio drives the face (audio_guidance_scale 2-3); prompt drives the
  body. num_inference_steps 15-25 (talking body). Chunked long-video via
  partial_video_length=113 + overlap 8.
- **Weights** (~9GB): Wan2.1-Fun-V1.1-1.3B-InP (VAE / T5-xxl / CLIP-ViT-H) +
  EchoMimicV3 transformer safetensors + wav2vec2-base-960h. `models/` layout
  mirrors infer_preview.py (config.yaml subpaths).

## Modal ops cheatsheet (EchoMimicV3)

- Deploy: `cd /root/projects/podsona && modal deploy modal/echomimicv3.py`
- Weights (once): `modal run modal/echomimicv3.py::download`
- App: https://modal.com/apps/billing-95875/main/deployed/podsona-echomimicv3
- Endpoint POST /render (JSON body, fields above) -> {"video_b64"}

## LongCat-Video-Avatar 1.5 pivot (2026-10-05) — PREMIUM two-person

Jay rejected the EchoMimicV3 quality bar outright ("premium only"). Research (3
parallel agent waves) established the decision tree and the final engine:

- **OmniHuman-1.5 = dead end.** Single-person everywhere (one image + one audio);
  even BytePlus's "multi-character" is per-mask render + stitch, not a native
  two-person frame. Not on OpenRouter. Official API = BytePlus (Vision AI,
  AK/SK HMAC, $0.16/sec) which Jay rejected for the hostile console.
- **lip sync.studio "InfiniteTalkMulti"** = the hosted winner (native two-person
  + per-speaker + clean key, $0.39/15s) but killed by a **$199 min API-credit
  buy-in** and a non-interchangeable user/API credit split. Also their submit
  endpoint returned "Internal Server Error".
- **OpenRouter has NO video/lip-sync/avatar model** (verified exhaustively: 466
  chat models + 57 image models, all image *edit/gen*, zero video output).
- **FINAL ENGINE = LongCat-Video-Avatar 1.5** (Meituan LongCat, MIT). Audio-
  driven multi-person video: `cond_image` (one two-person image) +
  `cond_audio.{person1,person2}` (two separate tracks) + `audio_type="para"`.
  Whisper-large-v3 lips (better than wav2vec2), 8-step DMD2 distillation + INT8,
  480p/720p. Its own eval pitches it vs HeyGen/Kling/OmniHuman-1.5. Native
  head/body motion + two-person interaction = the thing static-head lip-sync
  (lip sync.studio) can't do — the "better than them" angle.
- **Pipeline (15s clip)**: `composeTwoPerson` (FLUX-3 multi-ref via OpenRouter,
  host-LEFT + guest-RIGHT since LongCat auto-splits the image in half) ->
  `buildSpeakerTracks` (per-speaker 15s WAV, silence elsewhere) -> LongCat web
  endpoint (self-hosted Modal) -> store clip.mp4.
- **Deploy**: `modal/longcat.py`. Weights (`meituan-longcat/LongCat-Video` base +
  `LongCat-Video-Avatar-1.5` adapter, ~90GB) in Modal volume `longcat-weights`.
  Base model must be a SIBLING dir of the adapter dir (script loads `../LongCat-Video`).
  `torchrun --standalone --nproc_per_node=1 --context_parallel_size=1 --use_int8`
  on 1x A100-80GB. `--num_segments 5` ≈ 16.5s @25fps; `--use_distill --model_type
  avatar-v1.5` is required pairing (sets 8 steps, cfg 1.0). Output at
  `{output_dir}/ai2v_demo_1.mp4`.

## Modal SDK gotchas (this VPS)

- **Old SDK (client 1.6.1)**: GPU is the STRING form `gpu="A100-80GB"` (no
  `modal.gpu.A100(...)` attribute), single-GPU only.
- `@modal.web_endpoint` is DEPRECATED -> use `@modal.fastapi_endpoint(method="POST")`.
- `modal/multitalk.py` is stale (superseded by `modal/longcat.py`); ignore it.