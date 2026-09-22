# Invite Conversion + Free-Trial Card — Locked Spec

Decided with Jay 2026-09-19.

## Free trial pricing card
- Equal-height pay cards + a full-width horizontal trial card below them.
- Trial card CTA starts a TEAM monthly trial (14-day, card-required, full features, usage-capped).
- Post-trial downgrade is fine: if they end trial on the Individual tier, existing tier-based limits/entitlements already downgrade access (no extra code).

## Invite collision (existing Individual payer/trial invited into an org)
SINGLE-org model (NOT multi-org — Jay reverted the multi-org idea as over-engineered for the real frequency).

Flow:
1. Admin invites an email.
2. Detect: the email already runs an Individual plan (their own 1-seat org with an active sub or trial).
3. Mark them a distinct state "Individual subscriber — needs conversion" (visible to admin), instead of the current silent `skipped`.
4. On the person's side, accepting shows: "You have your own Individual plan. Join <org>? Your Individual plan ends when you join."
5. On confirm: cancel their Individual Stripe sub (prorate), dissolve their personal 1-seat org, assign them to <org> as a member.
6. Learning progress/XP carries over automatically — XP is keyed to the USER (users.total_xp, module_progress.user_id), not the org. Nothing is lost.
7. Joining consumes one of <org>'s seats (existing activation = seat-paywall already enforces this).

### Implementation notes (from code audit)
- Detection hooks into the member-import/invite path. Multiple onboarding paths exist: SSO JIT (`provisionUser` in data.ts, used by `/api/auth/entra/callback`), CSV import (`/api/admin/users/import`), and the invite/activate action (`/api/admin/members` POST invite → signInviteToken + set-password). Must trace which path surfaces "skipped" today and hook detection there.
- Stripe cancel + prorate: NO existing `cancelSubscription` Stripe call — only `markSubscriptionCanceled` (DB-only). Needs a new Stripe-backed cancel (graceful no-op until keys land).
- Org dissolve: NO existing `deleteOrganization`. Needs a new "dissolve empty 1-seat org" path (reassign the user first, then delete the now-empty org + its cascades).

## Update 2026-09-19 — "keep my plan" escape hatch
The accept page is a TWO-way choice, not a single convert:
- Primary: "Join <org>" (cancels Individual sub + dissolves personal org + joins; XP carries, user-keyed).
- Secondary: "Keep my Individual plan" = move the Individual account to a different (personal) email (re-encrypt email per createUser, uniqueness-checked, revoke sessions, verify new email), then re-provision the freed org email as a fresh member (set-password invite) into <org>. Requires a new account email-change capability (none exists today).

## Status
- Trial card: ✅ SHIPPED + LIVE (commit `dd847ab`).
- Conversion flow (dual option): ✅ SHIPPED + LIVE. `a74aa30` (Individual-plan conversion flow), `2e1d192` (click-to-confirm email change for keep-Individual-plan), `92137d9` (cancel subscription + rate limiting). Accept page = `/join-org` (Join org OR Keep my Individual plan); convert endpoint = `/api/invite/convert`; `needs_conversion` state in roster + CSV import; `dissolveOrganization` + `cancelSubscription` wired. Prod deployed at `d2b78b03` (HEAD).
- SSO JIT detection: ✅ SHIPPED + LIVE (`14aefa9`). Entra SSO callback now flags Individual-plan holders as `needs_conversion` (via shared `isIndividualPlanHolder` = active sub/trial, not bare `plan_tier`) instead of silent `org_conflict`; CSV import uses the same precise detection (free accounts stay `skipped`).