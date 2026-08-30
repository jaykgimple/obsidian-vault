---
title: LucentSkill — AI Upskilling LMS
created: 2026-08-30
tags: [property, lucentskill, lms, ai]
status: active
aliases: [LucentSkill Platform, lucentskill]
---

# LucentSkill

> AI upskilling LMS. Prism (AI) authors courses, surveys assess readiness, admins assign learning by segment.
> Repository: `/root/projects/lucentskill` · Live: lucentskill.com (Neon Postgres)
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router) |
| Backend | Raw Postgres (pg Pool, no ORM) |
| DB | Neon (DATABASE_URL in .env; NOT local) |
| Auth | jose JWT, roles `owner` > `admin` > `member` |
| AI | Prism (LongCat 2.0 / gpt-4o-mini for simple) |
| Email | Resend (dedicated subdomain, never root) |

## Key Modules

- Survey engine + readiness assessment (Typeform/Qualtrics bar)
- Prism course authoring + version/draft buffer
- Smart Assignments (segment targeting, audit log)
- Content Library (reusable blocks by reference)
- Notifications (in-app + email, per-type prefs)

## Status

- Live, actively developed (2026-08). Gauntlet loop is the standard build flow for features.
- Bar: WorkRamp for teams/roles + course authoring.

## Recent Work

- [[LucentSkill-Teams-Scoped-Content]] — team entity + delegated lead (in flight)

## Notes

- Hard rule: update `src/lib/docs.ts` registry for EVERY feature.
- No em dashes in any copy/comments. Neutral multi-tenant terms (never "badge" → "identifier").
