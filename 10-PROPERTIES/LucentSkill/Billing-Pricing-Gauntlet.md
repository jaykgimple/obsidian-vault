# Billing & Pricing Gauntlet — Locked Spec

Status: IN PROGRESS (gauntlet loop, builder/critic subagents only)

## Decision log (all confirmed by Jay)
- 3 tiers: Individual / Team / Enterprise. Prices round, monthly-first, annual in parens.
- Individual $15/mo or $150/yr. Single seat, no org, no members. Full security.
- Team $12/user/mo or $120/user/yr ($10/user/mo annual). Per seat, no minimum. Full features.
- Enterprise $150/user/yr, annual only, 250 seat minimum.
- Security NEVER gated by tier: MFA, encryption-at-rest, GDPR, prompt-injection on all tiers.
- SSO + audit log = premium Team ADD-ONS (not Enterprise-only).
- Add-on pricing (flat per org, not per-seat): SSO $50/mo or $500/yr; Audit log $25/mo or $250/yr. Enterprise includes both.
- Trial = card-required 14-day time trial, full features but usage-capped.
- Individual guard = 40 AI actions OR $5 spend, whichever first.
- Support = 5 business days, founder-direct. No 24/7, no onboarding/CSM promise.
- DPA = take-it-or-leave-it, automated self-serve signing (free, DocuSign-like) + audit trail + PDF.

## Usage meters (single usage_events table)
1. ai_action — any AI call (assessment, generation, assignment plan, survey gen/analysis, grading)
2. course_generation — content generation (heaviest; on trial capped separately)
3. course_taken — course enrollment/consumption (content access guard)
4. spend — actual token cost in cents (hard backstop)

## Limits
- TRIAL (14d): course_generation 2, course_taken 3, ai_action 10, spend $2.00. Whichever first.
- INDIVIDUAL: ai_action 40/mo, spend $5.00/mo, course_taken unlimited (generation counts within ai_action).
- TEAM: ai_action ceiling 5000/mo, spend $500/mo backstop, course_taken unlimited.
- ENTERPRISE: no caps (ai_action + spend = null/uncapped, still tracked). "Only Octogentic" org = enterprise, id dfb1e327-...aab66c.

## Gauntlet rounds (actual)
1. Foundation: migration 035 + pricing.ts + entitlements.ts + usage.ts ✅ OURS_WINS (5e67660)
2. Stripe backend: stripe.ts + billing.ts + checkout/portal/webhook ✅ OURS_WINS (aaf1074)
3a. Public pricing page + billingClient + nav ✅ OURS_WINS (7c54596)
3b. Admin billing page ✅ OURS_WINS (61b2463)
4b. AI usage enforcement (live OpenRouter price refresh) ✅ OURS_WINS (97ac861)
5a. Add-on persistence (migration 036 addons) ✅ OURS_WINS (89e2d72)
5b. Entitlement gating (SSO/audit/member, server-side) ✅ OURS_WINS
5c. Member import unlimited / activation=seat paywall (migration 037 invited_at) ✅ OURS_WINS (0a55ba0)

## Seat + cap model (final)
- IMPORT = unlimited (never rejects). ACTIVATION/SEND-INVITE = the seat paywall (prompt 'add seats').
- Individual: canInviteMembers=false (no members at all). Team: seatLimit=subscription seats. ENTERPRISE: seatLimit null (uncapped, no usage caps either). Trial: full entitlements, seatLimit null, usage-capped only.
- Octogentic org = enterprise (id dfb1e327-9923-4bba-9eb0-f5cf5aaab66c), exempt by construction.
- Count denominator = countInvitedUsers (users.invited_at NOT NULL); owner marked invited at bootstrap.

## Remaining
- STRIPE ACTIVATION (blocked on Jay's keys 2026-09-20): create Products/Prices, wire STRIPE_PRICE_* + STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET, live checkout/webhook test.
- DPA + signing: DEFERRED (post-launch).

## Deployment note
Full Stripe activation gated on API keys (Jay supplies 2026-09-20). Everything else builds/deploys today.

## Env vars (Stripe, for tomorrow)
- STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_* (product/price IDs), NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY