# LucentSkill — Security Gauntlet (Backlog) Progress + Encryption-at-Rest Rollout

Date: 2026-09-19

## Gauntlet status (security backlog gauntlet, bar = OWASP ASVS/NIST/RFC)

Done + live on www.lucentskill.com:
1. MFA (TOTP) — optional-by-default, org `mfa_required` admin step-up.
2. MS Entra SSO — org BYO tenant, OIDC auth-code + PKCE, org-scoped identity (no ATO), admin config UI in org settings.
3. Session revocation — per-user `session_epoch` kill switch, admin recertification surface.
4. Failed-login / auth-event audit logging — `auth_events` table, append-only, admin viewer, domain->org attribution.
5. Semantic prompt-injection classifier — two-layer (L1 regex + L2 free-LLM) in front of Prism + grading.
6. Encryption-at-rest — AES-256-GCM for PII (below).

Remaining (queued): 7 (CI security gates), 8 (GDPR consent/DPA/retention).

## Final status (all 8 DONE + live, 2026-09-19)

7. CI security gates — .github/ workflows: CI (tsc+build+npm audit HIGH), CodeQL, Dependabot, gitleaks secret-scan, dependency-review + SECURITY_CI_CHECKLIST.md for owner-only toggles (secret scanning/push protection/branch protection). Not a Vercel deploy (GitHub-only).
8. GDPR readiness — consent_records (migration 034) + server-side consent gate on signup, privacy/terms transparency, /api/me/export + org-scoped admin export (Art 20), comprehensive erasure (Art 17) incl. roster-wipe-independent-of-org, retention schedule + records-of-processing (Art 5/30) with honest DPA note.

## Encryption-at-rest — what was encrypted

Randomized AES-256-GCM (non-searchable): survey_responses.answers (JSONB->TEXT), users.display_name, organizations.primary_contact_name/phone.
Deterministic AES-256-GCM (equality-preserving): users.email, roster_entries.email, course_shares.recipient_email, blog_subscribers.email.
HMAC blind index: users.email_domain_hash (for domain->org resolution).

## Key management

- DATA_ENC_SECRET (32-byte base64, KEK) lives in `/root/projects/lucentskill/.env.local` AND Vercel prod+preview env (type=encrypted). NEVER committed to git.
- Key parity verified end-to-end (live signup ciphertext == local encryptDeterministic output).
- Migration 033 (email_domain_hash column + answers JSONB->TEXT) applied; backfill `--apply` ran; round-trip verified; plaintext backup shredded.
- Deploy-safe: plaintext fallback on equality lookups, so no deploy-order bomb.

## Lesson (repeat of a standing rule)

Migration 033 was NOT applied before the code deploy -> signup returned 500 (createUser inserted `email_domain_hash`, column absent). Rule: `npm run db:migrate` BEFORE push/deploy, every time. The "encrypted" label in `vercel env` does NOT prove the value is non-empty — verify at RUNTIME (here: a live signup + ciphertext parity check).