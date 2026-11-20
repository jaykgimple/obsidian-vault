---
title: QA Feedback Widget
created: 2026-11-19
tags: [lucentskill, feedback, qa, feature]
status: live
---

# QA Feedback Widget (LucentSkill)

Part of → [[LucentSkill]]

## What it is

A floating feedback button (bottom-right, every page) for QA/testing. Testers capture a screen (with a draw-on annotation canvas), pick a type + severity, write a comment, add labels, and submit. The site-admin console triages it; a keyed agent API lets the agent read it programmatically.

## Anatomy

- **Enablement is two-dimensional** (both must be on for an org to see it):
  1. Global master: feature flag `feedback_enabled` (default true) in `platform_feature_flags`, toggled in `/site-admin/flags` and on the feedback page.
  2. Per-org opt-in: `organizations.feedback_enabled` (default false), toggled in `/site-admin/feedback` → "Org access".
  - Anonymous viewers are hidden unless the page URL carries `?lumenqa=1` (QA hook; still gated by the global flag).
- **Widget** `src/components/FeedbackWidget.tsx` (mounted in root layout): type (bug/feature/idea/ux/content/other), severity (low/med/high/critical), title, comment, labels, screen capture via `html-to-image` + annotation canvas (pen/arrow/rect/text, 4 colors, undo/clear), and auto-captured browser + console.error/warn context.
- **Storage** `src/lib/feedback.ts` → `feedback` table (migration 045). Screenshot is a compressed base64 JPEG in a text column (no R2 hop); `user_email` is plaintext by design (their own contact, readable without decrypt).
- **APIs**:
  - `GET /api/feedback/config` + `POST /api/feedback` (public; rate-limited 10/min/IP, CSRF + enablement fail-closed).
  - `GET/POST /api/site-admin/feedback`, `GET /api/site-admin/feedback/[id]`, `GET/POST /api/site-admin/feedback/orgs` (audited, MFA-gated writes).
  - `GET /api/v1/feedback` — agent read API, bearer `FEEDBACK_AGENT_TOKEN` (filters: status/type/orgId/since/limit/offset/withScreenshot).
- **Admin UI** `/site-admin/feedback` (nav card on the site-admin dashboard): Inbox (filter by status, expand a row for full screenshot + console + env + triage status/labels) and Org access (per-org toggles).

## Status + knobs

- Live (2026-11-19). Build green, 207/207 tests pass.
- `feedback_enabled` global flag defaults TRUE but no org has `feedback_enabled` yet, so nothing shows until an org is opted in (site-admin → QA Feedback → Org access).
- Agent read API is 503 until `FEEDBACK_AGENT_TOKEN` is set in Vercel env. Token generated + stored in `pass` at `lucentskill/feedback-agent-token`.

## Usage (agent)

Read new feedback / triage:
```bash
TOKEN=$(pass show lucentskill/feedback-agent-token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.lucentskill.com/api/v1/feedback?status=new&withScreenshot=1"
```
