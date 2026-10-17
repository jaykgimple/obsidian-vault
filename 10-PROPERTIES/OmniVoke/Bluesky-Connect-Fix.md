# Bluesky Connect — Fix (2026-09-29)

## Symptom
Connect flow showed "Not connected" no matter what. User tried two handle forms (with and without `@`).

## Root cause (three defects)
1. **No verify-on-save.** `POST /api/integrations` created the row as `status: "disconnected"` and never logged in. Only YouTube/LinkedIn had a real connect step (the OAuth callback set `status: "connected"`). Bluesky (and every other BYO-key platform) was a silently-dead drop.
2. **Credential field mismatch.** The app password was stored in `clientSecretCipher`, but the Bluesky publish adapter reads it from `accessToken` (which maps to `accessTokenCipher`). The publish engine throws `not_connected:{id}` when `accessTokenCipher` is null — so even a "connected" Bluesky account could never publish.
3. **No handle normalization.** `createSession` rejects a leading `@`. The user's two-connection test (`@handle` vs `handle`) was probing exactly this.

## Fix
- `src/lib/bluesky.ts`: added `normalizeBlueskyIdentifier` (strips leading `@`, trims, preserves `did:`); applied inside `blueskyCreateSession` so every login path benefits.
- `src/app/api/integrations/route.ts`: on Bluesky save, do a real `blueskyCreateSession` login; store the app password in `accessTokenCipher` (the field the engine reads) and the refresh JWT in `refreshTokenCipher`; set `status: "connected"` on success, `status: "error"` + surfaced reason on failure.
- `src/app/dashboard/page.tsx`: on a Bluesky `error` result, keep the modal open, retain the entered values, and show the reason inline so the user can fix and retry (instead of landing on a silent "not connected" row).

## Verified
- tsc clean; build green; 2 new unit tests pass (normalizer + `@`-strip on login); pre-existing 3 unrelated env-missing-key test failures unchanged.
- Deployed READY (commit 88b895e). Live: / and /setup 200, /dashboard 307 (auth), PDS describeServer reachable.

## Lesson
Bluesky uses app passwords, not OAuth. "Save" IS "connect" for BYO-key platforms — it must verify and set connected/error, never leave a silent disconnected row. app password → accessToken, handle/DID → clientId.