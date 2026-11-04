# RoleFresh

Property-level status, updated 2026-10-19.

## Growth gauntlet: 8/8 shipped

Blind-builder + blind-critic loop (each piece ships only on a blind OURS_WINS).
All committed to main and deployed to rolefresh.vercel.app.

| # | Piece | Bar | Live check |
|---|---|---|---|
| 1 | Funnel/activation analytics (FunnelEvent + /api/admin/funnel) | PostHog | 401 unauth |
| 2 | Onboarding checklist + dominant empty-state CTA | Linear | dashboard |
| 3 | Social proof (honest mechanism proof, no fabricated metrics) | Stripe | landing |
| 4 | Publish 30-post layoff series | - | ON HOLD (OmniVoke key) |
| 5 | Email lifecycle (welcome / score follow-up / win-back cron / landed-share) | ReallyGoodEmails | cron CRON_SECRET |
| 6 | OG share image (Geist, green, correct claims) | Vercel/Linear | og-image.png |
| 7 | Referral moments (score-improvement + first-interview share nudges) | Dropbox/Notion | ShareNudge |
| 8 | Dynamic per-layoff landing | campaign landing | /layoffs/[slug] = 200 |
| 9 | Admin activation-funnel analytics + AI interpretation | PostHog | /dashboard/admin/analytics = 200 |

## Layoff pipeline (live, end to end)

- WARN scan (scripts/layoff_scan.py) pulls warnacttracker.com (current 2026
  notices, ~1639 records, stable notice_id), dedups by seen_ids.json, upserts
  large cohorts (affected >= 100) into Neon OutreachCohort via raw SQL.
- 510 cohorts in the table as of 2026-10-19.
- /layoffs/[slug] computes slug on the fly (slugifyCompany), aggregates
  multiple notices per company (sum affected, most-recent effectiveDate).
- 30-post series + 15-day plan live as JSON in content/layoff-series/queue/,
  NOT yet published (blocked on OmniVoke).

## Key facts

- Neon project: one per product. RoleFresh DB via DATABASE_URL in .env.
- Pricing: Landed (free) / Pro ($14.99/mo) / Lifetime ($129). Referral $20 off.
- Grounded capabilities ONLY: resume parsing, ATS+recruiter scores, keyword
  targeting, verbatim bullet rewrites, tailored cover letters/outreach,
  pipeline tracking. Does NOT find/recommend/match jobs or scrape.
- No em dashes in any copy. Brand green #10b981/#34d399. No provider/model names.

## Feedback gauntlet + recruiter red flags (2026-11-04)

Matt's 10 feedback rows → 3 buildable pieces (pricing parked). All shipped to prod.

- **P1 resume parser** (`structured-resume.ts`): wrapped bullets join, org+role
  grouping survives page breaks, promotions inherit company/dates, whitelist-free
  title detection, terminal-range guard (no text drop), dash-separated education.
  5 builder/critic rounds, OURS_WINS. Commit d55822b.
- **P2 intake** (`resume-intake.ts` + `resume-score.ts`): answers persist by
  stable id (questions generated once), intake-grounded `candidateSpecifics`
  raises ONLY the `quantified` dimension (no bulletStrength/ATS pollution, no
  fabricated delta, rawText never mutated). Added `intakeQuestions` column via
  prisma db push. Commit b7f991e.
- **Recruiter red flags** (partner video, Cody Brooks "Claude transforms resumes"):
  deterministic `redFlags` on both cards (why a reviewer passes), generic-filler
  detection, summary gains a "passing would be a regret" close. Flags injected
  into every rewrite prompt as "eliminate these" targets; editor passes live
  flags automatically. Commit 70eeadd.

## Open items

- Publish the layoff series + 15-day plan (blocked on OmniVoke API key from Jay).
- Deferred residuals in docs/GAUNTLET_PROGRESS_GROWTH.md (non-blocking).
- P3 dashboard font scale from Matt's feedback (3440×1440 readability) NOT started.