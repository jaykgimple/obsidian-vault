---
title: RoleFresh — Job Matching Platform
created: 2026-06-27
tags: [property, rolefresh, jobs]
status: active
aliases: [RoleFresh Platform, Resume Tool]
---

# RoleFresh

> Job matching web platform. Users upload resumes, AI tailors applications.
> Repository: `/root/projects/rolefresh`
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (Vercel) |
| Backend | Supabase (shared with Story Engine / Fantasy Stack) |
| AI | Resume tailoring, job matching |

## Status

- Live at: rolefresh.vercel.app
- Supabase project: **jobbox-os** (`sabexijntgtwflthkzdh`, us-east-1) - not shared with Bookbrary (that note is stale)
- Development priority: **paused** (user focusing on OctoGentic + Story Engine)

## 🚨 Active Blocker: Supabase DB unreachable (since ~Sep 6)

- Direct DB listener (`db.sabexijntgtwflthkzdh.supabase.co:5432`, IPv6 `2600:1f18:7d97:f601:a70b:3206:2145:7b95`) returns `ECONNREFUSED` at TCP level (not an auth/password issue).
- Cascades to everything: management API SQL runner, postgREST (REST API returns `PGRST002` schema-cache 503), pooler Supavisor (`ENOTFOUND tenant not found`), and the daily job scraper (zero inserts since 05:07 Sep 8).
- Supabase project status reports `ACTIVE_HEALTHY` but the `db` service health is `UNHEALTHY`. Auth (GoTrue) still healthy.
- Matches known Supabase class of issue: Pooler/SQL-runner cannot reach DB over IPv6 (see supabase discussion #41324).
- **Fix owner:** Jay (needs Supabase-side intervention; not recoverable from local creds).
- **Status 2026-09-14:** Still down. Fresh Bytes cron run wrote + queued "You Don't Need to Be an AI Engineer..." (Tips & Tricks, 1270 words); confirmed postgREST `PGRST002` (schema-cache, DB unreachable), management-API SQL runner throttled/refusing, stale `sb_secret_ShCb3...` key invalid. 6 posts now queued in `scripts/pending_fresh_bytes_post*.json`. Fix still owned by Jay.
- **Status 2026-09-15:** Still down. Confirmed at TCP/pooler level: `aws-1-us-east-1.pooler.supabase.com` returns `EAUTHQUERY (authentication query failed: connection to database not available)`, management-API SQL runner still `429 ThrottlerException`. Fresh Bytes cron run wrote + queued "The 2026 Comeback..." (Triumphs, 1258 words) → `scripts/pending_fresh_bytes_post_2026-comeback.json`. 7 posts now queued. Fix still owned by Jay.
- **Status 2026-09-18:** Still down. Project still reports `ACTIVE_HEALTHY` via management API but `db` service unreachable. Re-confirmed all paths fail: management-API SQL runner `429 ThrottlerException` + `ECONNREFUSED 2600:1f18:7d97:f601:a70b:3206:2145:7b95:5432`; pooler `EAUTHQUERY (connection to database not available)`; postgREST anon `503` (schema-cache). Fresh Bytes cron run wrote + queued "The Ghosting Epidemic..." (Troubles, 1268 words) → `scripts/pending_fresh_bytes_post_ghosting-epidemic.json`. 8 posts now queued. Fix still owned by Jay.
- **Status 2026-09-20:** Still down. `db` health service confirmed `UNHEALTHY` (`ECONNREFUSED 2600:1f18:7d97:f601:a70b:3206:2145:7b95:5432`) even as project reports `ACTIVE_HEALTHY`. All publish paths re-verified failing: management-API SQL runner `429 ThrottlerException`; pooler `EAUTHQUERY (connection to database not available)`; postgREST `PGRST002` (schema-cache). Fresh Bytes cron run wrote + queued "The 2026 Salary Script..." (Tips & Tricks, 1211 words) → `scripts/pending_fresh_bytes_post_salary-script.json`. 9 posts now queued. Fix still owned by Jay.

## 📝 Latent issue: stale service_role key

- `.env.vercel` `SUPABASE_SERVICE_ROLE_KEY` (`sb_secret_ShCb3...`) is stale: it hashes identically to Bookbrary's key, but jobbox-os's current secret keys are `sb_secret_dccGm...` (default) and `sb_secret_hcR0g...` (temp_access, created 2026-08-28). Publishing must use the management-API SQL runner (personal access token), which also depends on the DB being reachable.

## 📄 Pending Fresh Bytes posts (publish once DB recovers)

- `scripts/pending_fresh_bytes_post.json` — "Application Fatigue..." (Troubles, ~Sep 1)
- `scripts/pending_fresh_bytes_post_ghost-jobs.json` — "Ghost Jobs Are Everywhere..." (Industry Trends, 1305 words, Sep 8)
- `scripts/pending_fresh_bytes_post_recruiter-ghosting.json` — "Radio Silence: Why Recruiters Ghost You..." (Troubles, 1359 words, Sep 9)
- `scripts/pending_fresh_bytes_post_ai-gatekeeper.json` — "AI Is Now the Gatekeeper..." (Tips & Tricks, 1210 words, Sep 10)
- `scripts/pending_fresh_bytes_post_ai-redundancy-washing.json` — "AI Didn't Take Your Job..." (Industry Trends, 1222 words, Sep 11)
- `scripts/pending_fresh_bytes_post_ai-fluency.json` — "You Don't Need to Be an AI Engineer..." (Tips & Tricks, 1270 words, Sep 14)
- `scripts/pending_fresh_bytes_post_2026-comeback.json` — "The 2026 Comeback..." (Triumphs, 1258 words, Sep 15)
- `scripts/pending_fresh_bytes_post_ghosting-epidemic.json` — "The Ghosting Epidemic: Why Recruiters Went Silent..." (Troubles, 1268 words, Sep 18)
- `scripts/pending_fresh_bytes_post_salary-script.json` — "The 2026 Salary Script: Negotiate Like You Have Leverage..." (Tips & Tricks, 1211 words, Sep 20)

## Agent Relevance

- Scraping agents (resume/job posting collection) → [[Key-Takeaways|Takeaway T-A2]] (autonomous error recovery)
- Tailoring agents → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Novelist|Agent: Novelist]] equivalent (prose generation)

## Compounding Notes

- RoleFresh's scraping retry logic → [[Self-Healing-Pipelines]]
- Anti-deskill protection (user noted) → [[Key-Takeaways|Takeaway T-C3]] from OctoGentic
