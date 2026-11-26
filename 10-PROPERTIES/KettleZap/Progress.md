# KettleZap: Build Progress

Status: MVP LIVE at https://kettlezap.vercel.app (auto-deploys on push to main).

## Done (2026-11-26)

- Repo: github.com/jaykgimple/kettlezap (private). Vercel project `kettlezap` under
  jaykgimples-projects, env DATABASE_URL + DIRECT_DATABASE_URL set (Neon project
  misty-mode-48622316, creds in `pass kettlezap/neon`).
- Movement library: `data/movements.json`, 32 movements, single source of truth.
- Form-demo videos: ALL 32 generated via `tools/generate_demo_videos.py`
  (Veo 3.1 Lite, 9:16 1080p silent, ~$12.80 total). Output `assets/demos/*.mp4`
  (gitignored). Resumable via `assets/demos/.jobs.json`.
  - Lesson: detailed formCue text in the video prompt tripped the provider content
    filter on floor / bent-over movements (racked-lunge, floor-press, bent-over-row,
    cleans, snatch, turkish-get-up, glute-bridge). Fix = generic instructional prompt
    (no formCue) + per-slug PROMPT_OVERRIDES for floor movements. After that: 32/32.
- Curriculum seed: `prisma/seed.js`, idempotent. 3 tracks x 30 days = 105 WorkoutDays
  (Advanced seeds 15 two-bell variants alongside the one-bell days), 1473 blocks.
  Timed days land 14.5-16.5 min. Run: `npm run db:seed`.
- Screens (all 5, Next 16 App Router, Tailwind v4 CSS-first theme):
  - `/onboarding` (3 taps: track, bell(s)+unit, sound; Advanced gets one/two-bell pick)
  - `/` Today (streak + totals strip, Today's Zap card, 30-day grid)
  - `/journey` (week bands, recovery days styled, locked future days)
  - `/zap/[day]` Player (hero timer, tap-to-advance reps, auto-advance timed,
    3-2-1 count-in, recharge previews with regression/progression + bell, pause veil,
    end-early confirm, giant controls)
  - `/zap/[day]/complete` (duration, blocks, streak, weights used, tomorrow teaser)
- Audio: Web Audio synthesized tones only (`src/lib/audio.ts`), unlocked on first tap.
- Auth: guest-first. Device cookie `kz_uid` -> anonymous User row; no email gate yet.
- Streaks/minutes DERIVED from WorkoutCompletion, never stored.
- E2E verified on prod build: onboarding -> day 1 -> player -> end early ->
  completion logged -> streak 1 -> day 2 next. Test user deleted after.

## Landing + auth (2026-11-26, second pass)

- `/` is now a public marketing landing (hero, how-it-works, 3 tracks, features, CTA).
  App home moved to `/today`. Logged-in users with bells auto-redirect from `/` to `/today`.
- Auth: email + password (Node scrypt, no deps) in `src/lib/auth.ts`; session = httpOnly
  `kz_uid` cookie. Pages: `/signup`, `/login` (shared `(auth)/AuthForm.tsx`).
- Guest-first preserved: "Try without an account" on the landing runs the old guest flow;
  guests see "Save progress" on Today, and signing up CLAIMS the guest row (progress kept,
  no duplicate user). Signed-up users without bells are routed back into onboarding.
- `User.passwordHash` added (migration 20261126023556_add_password_auth, applied to prod DB).
- `package.json` has `postinstall: prisma generate` (Vercel fresh installs do not run it
  otherwise; the first landing+auth deploy failed on stale Prisma types until this was added).
- Logout button lives in the Today header (LogOutButton.tsx); guests see Save progress instead.
- `AUTH_SECRET` generated for future magic-link tokens: vault `kettlezap/auth-secret`,
  set in Vercel env + local .env.
- E2E verified locally and on prod: signup, login, bad-password error, guest flow,
  guest-claim, onboarding dedupe. Test users deleted after.

## UX fixes + videos (2026-11-26, third pass)

- Sound toggle knob fixed: was absolutely positioned with no `left` anchor, so
  `translate-x-7` pushed it outside the oval. Now `left-1` + `translate-x-6` travel.
- Transition timer: after a block with no programmed Recharge, the Player inserts a
  gap (default 10s) labelled TRANSITION (vs RECHARGE for programmed rests). User-config
  on the Player start screen: 0/5/10/15/20/30, persisted to `User.transitionSec`
  (migration 20261126030112_add_transition_sec).
- Form-demo videos are now LIVE in the Player: looping <video> on the "First up" card
  and the Recharge/Transition "Up next" preview. Hosted in Cloudflare R2 (private), served
  via presigned GET URLs (SigV4, `src/lib/r2.ts`, zero SDK deps). The R2 token is scoped
  to the omnivoke-media bucket only (cannot create buckets), so KettleZap demos live under
  the `kettlezap/demos/` prefix there. Uploader: `tools/upload_demos_r2.py`.
- R2 creds in Vercel env (R2_ENDPOINT / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_BUCKET)
  and local .env; values from `pass cloudflare/r2/*`.
- Jay's own account `jaykgimple@gmail.com` has signed up and logged a completion on prod.

## Next

- Serve demo MP4s from R2 and wire into Player rest screens (in-app looping demos).
- Magic-link email sign-in (needs the Resend key: only copy lives in Vercel encrypted
  env for RoleFresh; Jay to paste it so it can be vaulted per the LinkedIn rule).
- Deploy check: no custom domain yet (kettlezap.vercel.app only).
