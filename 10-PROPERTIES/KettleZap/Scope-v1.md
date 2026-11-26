# KettleZap: Product Scope (v1, for review)

Status: DRAFT, awaiting Jay approval before any code.

30-Day, 15-Minute Kettlebell Workout Program. NeonDB + Vercel.

---

## 1. Vision

Help people build strength, endurance and lean muscle with nothing but a kettlebell,
15 focused minutes a day, for 30 days. The product wins on one thing: mid-workout
effortlessness. You drop the bell, you tap once, the audio tells you what to do.

North-star metric: Day-7 completion rate (share of users who finish 7 Zaps), the
classic habit-formation line. Secondary: streak length and completion rate.

## 2. Look & feel (the aesthetic contract)

- High-contrast dark mode: deep slate / charcoal base, electric yellow / lime accent.
- Optimized for glanceability from 5+ feet away on a mat: the TIMER is the hero,
  huge and monospaced, the rest of the screen recedes.
- Minimal taps. One primary action per screen. Everything else behind a disclosure.
- Brand language (do not invent alternatives):
  - Daily workouts = "Daily Zaps"
  - Rest intervals = "Recharge"
  - Streaks = "Charge Streaks"
- WCAG 2.2 AA as the floor (contrast of accent on slate, focus-visible on every
  tappable, large hit areas, reduced-motion honored).

## 3. Three tracks

Same 30-day, 15-min, 4-week skeleton. Only the movements, load and Recharge density
change. Users pick at onboarding and can switch later (progress is per-track, but a
switch starts a fresh streak rather than wrecking the old one).

- Beginner "Foundation": two-hand swing, goblet squat, deadlift, strict press,
  bent-over row, farmer carry. One light bell. EMOM-heavy, 45-60s Recharge, low reps,
  form cues everywhere. Goal = make the six fundamentals automatic.
- Intermediate "Metabolic": single-arm swing, clean & press, snatch, renegade row,
  lunge variations, Turkish get-up (light), halo. Mix EMOM + AMRAP + timed HIIT.
  30-45s Recharge. Goal = conditioning + power under fatigue.
- Advanced "Peak": double-bell complexes (clean + squat + press), heavy snatch,
  long EMOM chains, HIIT ladders, minimal rest (15-30s). Goal = max density and
  intensity with clean-ish form held together.
  Advanced offers a ONE-BELL or TWO-BELL option (user picks at onboarding): a
  single-bell day and a double-bell day are both seeded where they differ, and
  the player routes to the matching variant.

## 4. User journey & screens (5 screens, nothing else)

1. Onboarding (one time, 3 taps):
   - Pick track (Beginner / Intermediate / Advanced, each shows its 30-day arc in one line).
   - Enter available kettlebells: weight + unit (kg/lb), can add more than one.
   - Sound on/off (default on).

2. Today (home = dashboard):
   - Big "Today's Zap" card: day number, phase, format, one-line focus, "Start Zap" button.
   - Charge Streak counter + total minutes this program (compact strip).
   - The 30-day grid lives here too (scroll): week bands with phase names, done = filled, today = pulsing.

3. Journey (the 30-day map, reachable from Today):
   - Full 4-week grid. Week bands labeled Foundation / Metabolic / Strength Complexes / Peak Intensity.
   - Every 7th day styled as Recovery/mobility. Tap a past day = preview or replay; future days = locked with a light reveal.

4. Player (the core screen):
   - Hero countdown timer (work vs Recharge in different accent states).
   - Current movement name + rep/time target, huge and glanceable.
   - Tap to advance rep-based sets; timed blocks auto-advance.
   - Audio: 3-2-1 countdown beeps, distinct "go" tone, transition chime.
   - Rest-screen preview: movement coming next, one-line form cue, easier ("regression") and harder ("progression") options, and a "swap weight" tap.
   - One-tap pause / end-workout, reachable without looking (giant fixed button).

5. Complete:
   - Duration, Zap done, sets/movements hit, weight used (editable), streak incremented.
   - "Tomorrow's Zap" teaser + "Log next workout" felt effortless via a single close.

Deliberately NOT separate screens: settings, profile, history list (folded into Completion + a lightweight history drawer), social/sharing.

## 5. Curriculum structure (the content asset)

Physically: 2 min warm-up + 13 min main circuit = 15 min hard cap. Recovery every 7th
day (Day 7/14/21/28) = mobility, still 15 min.

- Week 1: Foundation & Form
- Week 2: Metabolic Conditioning
- Week 3: Strength Complexes
- Week 4: Peak Intensity

Formats supported per block: EMOM, AMRAP, timed HIIT, and MOBILITY for recovery.
Each movement carries: rep/time target, load tier (bodyweight / light / medium / heavy),
Recharge duration, form cue, regression, progression.

Seed data: 3 tracks x 30 days = 90 Zaps, each ~5-8 blocks. This is the single biggest
content effort. Authored once, stored in DB, never generated at runtime.

## 6. Data architecture (NeonDB)

Five tables. Streaks and all dashboard numbers are DERIVED from completions, never stored.

- users: id, email (nullable), name, unitPref (kg|lb), track (enum), soundOn, createdAt.
- kettlebells: id, userId, weight (number), unit, label (nullable), position. Unique on (userId, weight, unit).
- workout_days (static, seeded): id, track, dayNumber 1-30, weekNumber 1-4, phase, isRecovery, format (enum), title, focus. Unique (track, dayNumber).
- workout_blocks (static, seeded): id, workoutDayId, orderIndex, kind (warmup|work|recharge|cooldown), movement, load (enum), workSeconds (nullable), reps (nullable), rechargeSec, formCue, regression, progression.
- workout_completions: id, userId, workoutDayId, track, dayNumber, completedAt, durationSec, weightUsed (json). Index (userId, completedAt).

Weight model: a block stores an abstract load tier; the player maps tier to the user's
actual kettlebell and lets them tap to change. weightUsed captures the real lb/kg per
session for the "weight-used logging" requirement.

## 7. Tech stack & Vercel setup

- Next.js App Router (React Server Components for static content, client components for the player).
- Neon Postgres (one project, branchable) + Prisma for types and migrations. Seed the 90 Zaps via an idempotent Prisma seed script.
- Auth: guest-first with a lightweight account to claim. Details in open questions.
- Audio: Web Audio API synthesized tones, zero asset files. 3-2-1 beeps (three short tones), distinct "go" tone, recharge/transition chime. Unlock the AudioContext on first tap (iOS). Offline-capable, free, no latency.
- Hosting: Vercel (auto-deploy on push to main, same as RoleFresh/LucentSkill). Env vars: DATABASE_URL, DIRECT_DATABASE_URL, AUTH_SECRET (if auth).
- No provider branding or model names anywhere in copy/docs.

## 8. MVP vs nice-to-have

MVP (this is what "amazing out of the gate" requires):
- Onboarding (track + bells + units), Today with streak, the Player with timers + synthesized audio + rest previews (form cue, regression/progression), Complete with weight logging, the 30-day grid. Data persisted to NeonDB.

Nice-to-have (do not build in v1):
- Social, sharing, leaderboards.
- Video form demos / animated GIF walkthroughs (ships as links, not built).
- Custom workout builder, "pick a bell workout" library.
- Notifications / reminders (a cron + email; add only after the core habit loop proves out).
- Offline PWA install, Apple Watch / phone-lock-screen integration.

## Refinements (Jay, after review)

- Advanced: one-bell OR two-bell option (added above).
- Form demos: every movement gets a looping animation (animated GIF) showing how
  it is done. Generated procedurally as an on-brand dark-background stick figure
  with the electric accent, looping. In-app it renders live (crisp SVG/canvas);
  a GIF file is generated for each movement for portability/share.

## Open questions for Jay

1. Auth friction vs persistence: recommend guest-first (start immediately, anonymous device row in NeonDB) + email magic-link to claim. Agree, or full signup gate?
2. Track progress isolation: switching tracks starts a new streak (recommended) vs one merged streak. Which?
3. Curriculum authoring: I can author all 90 Zaps as seed data now, or start with Beginner + Intermediate complete and Advanced templated. Full = more upfront content work.
4. Video form cues: none in v1 (text only), or link out to curated demo videos?
