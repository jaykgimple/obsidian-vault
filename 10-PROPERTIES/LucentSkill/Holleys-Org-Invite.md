---
tags: [lucentskill, admin, invites, email, encryption]
created: 2026-09-28
---

# Holleys Org + On-Demand Invite Sender

## What shipped
- **Holleys org** provisioned in prod, `plan_tier=enterprise` (matches the free reference org: no trial, no sub, no Stripe customer = unbounded seats + premium features included).
  - jcholley@gmail.com = owner
  - etnholley@gmail.com = admin
  - lynash05@gmail.com = admin
  - All `invited_at` set; default AI Readiness Assessment seeded.
- **New secret-gated endpoint** `POST /api/admin/invite-org` (`INVITE_ADMIN_SECRET` bearer), backed by `src/lib/orgInvite.ts` `sendOrgInvites(orgSlug)`. Sends a fresh set-password invite email to every dormant (`last_login_at IS NULL`) member of one org, on demand. Not wired to a cron (manual one-shot by design).

## How to fire it (operator)
```bash
SECRET=$(cat /root/projects/lucentskill/.invite_admin_secret)
curl -s -X POST "https://www.lucentskill.com/api/admin/invite-org" \
  -H "Authorization: Bearer $SECRET" -H "Content-Type: application/json" \
  -d '{"orgSlug":"holleys"}'
```
Secret value lives ONLY in `/root/projects/lucentskill/.invite_admin_secret` (gitignored) and Vercel `INVITE_ADMIN_SECRET` (encrypted). Hit `www.lucentskill.com` directly; `curl -L` from the apex drops the Authorization header across the 308 host redirect.

## Lesson: email is encrypted AT REST
`users.email` (deterministic, col `users.email`) and `users.display_name` (randomized) are stored as `enc:v1:…` ciphertext. Any raw SQL that reads these and passes them to `send*Email` must decrypt first via `decrypt(v, "users.email")` / `decrypt(v)` from `src/lib/crypto.ts`. The app's typed helpers (`getUserByEmail`) decode transparently, but hand-written `getPool().query` calls do NOT.
- Fixed in `src/lib/orgInvite.ts` AND `src/lib/reengagement.ts` (the weekly re-engagement cron had the SAME bug — would have emailed ciphertext). Commit `7d0bc0b`.

## Repo state
- `src/lib/orgInvite.ts`, `src/app/api/admin/invite-org/route.ts`, `src/lib/reengagement.ts` (decrypt fix), `.gitignore` (+ `.invite_admin_secret`).
- All committed/pushed, deploys READY, `tsc` clean, reengagement tests green (4/4).