---
title: Daily Lumen Blog
created: 2026-09-18
tags: [lucentskill, blog, content, automation]
status: active
aliases: [Daily Lumen, LucentSkill Blog]
---

# Daily Lumen (blog)

> Part of → [[LucentSkill]] ← [[Home]]
> Date: 2026-09-18

## What it is
Auto-published daily blog for LucentSkill. Cadence: every day at 14:00 UTC via `/api/cron/generate-blog`. No skip days (falls back to a fresh-lens deeper dive on a prior post). Auto-publishes (no draft buffer). RSS 2.0 at `/rss.xml`.

## Pipeline
1. Poll 16 Tier-1 free AI-news sources (feeds in `blogSources.ts`).
2. Rank by relevance to the 4 pillars (AI training / readiness / workforce upskilling / benefits of upskilling).
3. Prism (deepseek-v3.2) writes ~1,200-word post + 5 takeaways.
4. Auto-publish -> DB row -> RSS updates -> daily email digest to subscribers.
5. Last paragraph ties the post back to lucentskill.com.

## Subscriptions + digest
- `blog_subscribers` table (migration 026). Public `/api/blog/subscribe` + `/api/blog/unsubscribe`.
- `sendBlogDigest` sends one Resend email per subscriber with a personalized unsubscribe token; wired into the cron (only when `published:true`).
- Scroll popup (~50% scroll, once per browser via localStorage) + inline form on `/blog`.

## Admin: create course from a post
Logged-in admins see a "Create course from this post" button on `/blog/[slug]`. It enqueues a Prism course generation grounded in the post (title/body/takeaways as sourceMaterial), mapped category -> track (AI Governance / ROI / Readiness -> strategist; Upskilling / Training / Tool Spotlight -> operator). Lands as a draft in `/admin/courses`.

## Content-quality fix (root cause + fix, keep permanent)
Bug: LLM emitted HTML entities (`&amp;`) and em dashes (`—`) in prose; `sanitize-html` re-encoded `&` on store; the blog markdown renderer escaped again -> literal `&amp;`. Em dashes surfaced on the listing via excerpts.

Fix (3 layers):
1. `guard.ts normalizeProse` = `decodeHtmlEntities` (safe set; deliberately does NOT decode `&lt;`/`&gt;`) + em-dash -> `, ` / en-dash -> `-`. Applied at generation in `blogGenerate.ts` + `courseStudio.ts` (SVG strings skipped).
2. Render backstop: `markdown.ts escapeHtml` runs `normalizeProse` before escaping.
3. One-time data fix `scripts/fix-blog-course-prose.ts` (idempotent) cleaned 10 posts + 5 courses in place.

Also swept em/en dashes from all UI copy + in-app docs (`docs.ts` titles now use `: ` delimiter, `DocsLayout` split updated to match).

LESSON: the fix belongs at GENERATION (so RSS/email/storage are clean) plus a RENDER backstop (so already-stored content renders correctly without a DB migration).
