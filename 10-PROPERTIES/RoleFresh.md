---
title: RoleFresh — Job Matching Platform
created: 2026-06-27
updated: 2026-10-11
tags: [property, rolefresh, jobs]
status: active
aliases: [RoleFresh Platform, Resume Tool]
---

# RoleFresh

> Job matching web platform. Users upload resumes, AI tailors applications.
> Repository: `/root/projects/rolefresh`
> Live: rolefresh.vercel.app
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router, Vercel) |
| Backend | Neon Postgres via Prisma (migrated off Supabase Oct 2026) |
| Auth | Auth.js v5 (Prisma adapter, JWT sessions, credentials + LinkedIn OAuth) |
| AI | OpenRouter (deepseek/deepseek-chat-v3.1 as DEFAULT_MODEL) |
| Payments | Stripe (subscriptions + one-time) |

## Status: ACTIVE

- Live at rolefresh.vercel.app.
- Migrated from Supabase → Neon in Oct 2026. The migration was **schema + code only**:
  Supabase (`jobbox-os`, sabexijntgtwflthkzdh) had been DB-down for ~26 days
  (TCP `ECONNREFUSED`, `db` service `UNHEALTHY`), so no user rows could be pulled.
  Neon started **empty** (0 users / profiles / plans). See archived incident note.
- Neon project: `ep-patient-bread-b4etkovq` (`neondb_owner`). DATABASE_URL in `.env`.
- Development priority: **active** (was "paused"; resumed Oct 2026 with pricing rebuild).

## Pricing model (shipped Oct 2026, gauntlet vs Rezi)

Three tiers, `PlanTier` in `src/lib/pricing.ts`:

- **Landed** (free): premium model quality, capped. 10 rewrites, 5 cover letters,
  5 interview prep, 3 LinkedIn, ~20 resume intake, 25 tracked jobs. Scoring is
  deterministic and honestly **unlimited** (no LLM call to meter).
- **Pro** $14.99/mo: unlimited. Monthly-only (no yearly toggle).
- **Lifetime** $129 one-time: unlimited, with anti-abuse.

Gauntlet verdict: **OURS_WINS** on all three pieces (tier model + enforcement,
pricing surface + Stripe, lifetime anti-abuse). Bar was Rezi's free demo / $29 /
$149. Deliberately did NOT fake Rezi's "62% land interview / 4M users / logos"
social proof; that's a real, still-open trust-signal gap on the landing page.

Anti-abuse (lifetime): daily fair-use cap (400 AI calls/day, `LIFETIME_DAILY_AI_CAP`)
+ multi-identity resale detection. Identity is fingerprinted from the **candidate's
resume header** (name+email via `identityKeyFromResumeText`), NOT the account
profile. Flag is advisory only (`UserPlan.abuseFlag*`), never auto-bans. See
`src/lib/anti-abuse.ts`.

## Admin surface (shipped Oct 2026)

- `User.role` (`candidate` | `admin`). Authoritative `requireAdmin()` guard in
  `src/lib/admin.ts` (fresh DB read, fails closed). Enforced in middleware +
  admin layout + every `/api/admin/*` route (403).
- `/dashboard/admin` metrics: total users, signups (7/30d), sign-ins, active
  users, tier counts, lifetime users, admins, converted referrals, abuse flags,
  AI call volume. Sign-ins tracked via `SignInEvent` (JWT strategy leaves the
  Auth.js `Session` table empty, so this is the authoritative ledger).
- `/dashboard/admin/users`: searchable table; upgrade-to-lifetime, promote/demote
  admin (self-protected against demoting yourself).
- `/dashboard/admin/invites`: invite an email; existing user promoted instantly,
  new email auto-grants admin on register (consumed in the register transaction).
- Hidden from non-admins everywhere.

## Referral & growth loops (Oct 2026)

Referral reward redesigned from "$10 token credits" (dead: premium AI is on every
tier, so credits buy nothing) to **plan-value discounts**, paid-conversion only:

- `getReferralReward()` → `$20 off`. Referred user gets $20 off their FIRST paid
  plan (Pro OR Lifetime, minted as a one-time Stripe coupon at checkout).
- Referrer earns `$20 toward Lifetime`, stacking, capped at the $129 Lifetime
  price (7 conversions = free Lifetime). Balance: `UserPlan.referralDiscountThousandths`.
- Lifetime referrers (and any cap overflow) gift the $20 to the friend instead —
  "pay it forward." Awarded in `src/app/api/stripe/webhook/route.ts` (`awardReferralDiscount`).

Success-share loop: marking a tracked job **"Landed"** (new terminal pipeline
stage) opens a share-your-win prompt (`SuccessShareModal`) that mints a $20
gift code (`src/lib/success-share.ts`, `SuccessShareGift` table). Gift-only,
double rate-limited: once per landed job (`applicationId` @unique) + once per
account per rolling 365 days. Redeemed via `GET /api/success-share?redeem=<code>`
→ credits the redeemer's `referralDiscountThousandths`. LinkedIn share is
self-attested (no partner API); the gift-only + rate-limit rules are what make
that safe (a fake "landed" only discounts a future sale, never pays cash).

## Key gotchas

- Vercel builds run `prisma generate` only — **schema changes are NOT applied to
  Neon automatically**. The CoS applies additive DDL manually via `psql
  $DATABASE_URL` (confirmed pattern on the anti-abuse columns, admin tables, and
  the Oct 2026 `DailyAiUsageCounter` atomic-cap table).
- `npm run build` includes type-check; `npm test` = vitest (716 tests as of the
  admin ship). One UI test (`resume-editor-jd-paste`) is flaky under parallel
  load (5s cap) but passes in isolation — not a real failure.
- Admin role is cached in the JWT at sign-in: a freshly promoted admin must
  log out/in once for the nav item to appear (backend access is immediate).

## Security loop (Oct 2026 — COMPLETE)

Ran the full security loop (3 audit batches + 2 builder passes) against OWASP
ASVS v4 L2 / LLM Top 10 / API Top 10 / Web Top 10. All CRITICAL/HIGH closed or
triaged. Full ledger in `docs/SECURITY_PROGRESS.md`. Highlights:

- Closed: 3 BOLA/IDOR (pipeline/contacts/intake), LLM01 prompt-injection (JD +
  context now delimited + system message), SSRF on jobs/add, open-redirect on
  login, email CRLF injection, race conditions (lifetime cap + Stripe credits ->
  atomic), error-message leaks (~20 routes), webhook payment_status/idempotency.
- Dependency fixes: DOMPurify 3.4.17, xmldom 0.8.15.
- Secret hygiene: `.env`/`.env.neon` untracked + gitignored (DB password
  rotation STILL REQUIRED — leak is in git history).
- Post-loop backlog (needs infra/product call): Next.js 14 -> 15.5.24+ major,
  persistent rate-limit store (in-memory Map is stateless on serverless),
  GDPR completeness (R2 binaries + Stripe customer on delete; free data export).

## Historical (archived, resolved)

- **Supabase DB outage** (Sep 6 – Oct 2026): `jobbox-os` DB unreachable, blocked
  the Fresh Bytes blog pipeline + app. Resolved by migrating to Neon. Details in
  [[Fresh-Bytes-Publish-Blocked-DB-Outage-2026-09-28]].
- Stale Supabase service_role key (`sb_secret_ShCb3...`) — moot post-migration.

## Agent Relevance

- Rewrite/tailoring agents → grounded in the candidate's master resume (truth
  grounding: never invent employers/metrics).
- Anti-abuse resale detection → candidate-identity fingerprinting.

## Compounding Notes

- Anti-deskill protection (user noted) → [[Key-Takeaways|Takeaway T-C3]] from OctoGentic.
- Scraping/retry self-healing → [[Self-Healing-Pipelines]].
