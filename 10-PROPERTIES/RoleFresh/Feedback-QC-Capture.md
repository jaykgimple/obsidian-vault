---
title: Feedback QC Capture
created: 2026-11-20
tags: [rolefresh, feedback, qc, feature]
status: live
---

Part of → RoleFresh

# Feedback QC Capture (RoleFresh)

Enhanced the feedback button with the LucentSkill QC kit, gated to enabled users only.

## Jay's ask

Port the QC features (screen capture + annotation, console capture, type/severity/labels/title) to RoleFresh's feedback button, but only for users it is enabled for. Plus an agent-read API and admin ability to view/manage QC messages.

## Enablement model (single-tenant, two-dimensional)

1. Global switch: `FeatureFlag` key `feedback_qc` (default ON). Admin toggles.
2. Per-user: `User.isFeedbackTester` (boolean). Admins are ALWAYS effective testers. Anonymous public-page QA via `?lumenqa=1` (still gated by the global flag).

Non-testers keep the simple category+message form; testers get the full capture.

## What shipped

- Schema (`prisma db push`, additive): `User.isFeedbackTester`, `Feedback` QC columns (title/severity/labels/screenshot/browser/consoleLogs), new `FeatureFlag` model.
- `src/lib/feedback-qc.ts`: `getFeedbackQcConfig`, validators, flag helpers.
- APIs:
  - `GET /api/feedback/config` (+ `?override=1`)
  - `POST /api/feedback` (QC fields stripped unless enabled)
  - `GET /api/v1/feedback` (agent read, bearer `FEEDBACK_AGENT_TOKEN`)
  - `GET/POST /api/admin/feedback/qc` (toggle global + add/remove tester)
  - `GET /api/admin/feedback/[id]` (full detail incl screenshot)
- Widget `src/components/FeedbackWidget.tsx`: QC mode with `html-to-image` screen capture + annotation canvas (pen/arrow/rect/text) + console.warn/error capture + severity/labels/title.
- Admin `/dashboard/admin/feedback`: QcPanel (global toggle + tester management) + per-item severity/labels/screenshot/console rendering.

## Tokens / creds

- `FEEDBACK_AGENT_TOKEN` → Vercel env (encrypted) + pass store `rolefresh/feedback-agent-token`.
- Vercel project `prj_7TeRsCEzPBh0fIbcXq28yLDilela`, team `team_kMfT49TlO1mtYuzRUc9HLolN`.

## Verified

Anonymous non-tester QC fields are stripped; `?override=1` stores them. Agent API 200 with token, 401 without. Build green; tests 983 pass (1 known pre-existing failure in `rewrite-summary.test.ts`, unrelated).

## Gotcha

RoleFresh has no raw `pg` dependency (Prisma-only); use `npx prisma db execute --stdin` for raw SQL, not `require("pg")`.

## Element inspector (added)

QC form has a "Pick an element" action: inspect mode highlights the hovered element and click/right-click captures its fingerprint into the report: tag, id, className, role, ariaLabel, text, a unique CSS selector path, and best-effort React component name (dev builds only; production strips `__reactFiber$`, so `component` is null there). Stored in `Feedback.element` (Json). This is the grep-key for the agent to locate the exact component when fixing bugs.

