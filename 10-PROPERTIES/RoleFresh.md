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

## 📝 Latent issue: stale service_role key

- `.env.vercel` `SUPABASE_SERVICE_ROLE_KEY` (`sb_secret_ShCb3...`) is stale: it hashes identically to Bookbrary's key, but jobbox-os's current secret keys are `sb_secret_dccGm...` (default) and `sb_secret_hcR0g...` (temp_access, created 2026-08-28). Publishing must use the management-API SQL runner (personal access token), which also depends on the DB being reachable.

## 📄 Pending Fresh Bytes posts (publish once DB recovers)

- `scripts/pending_fresh_bytes_post.json` — "Application Fatigue..." (Troubles, ~Sep 1)
- `scripts/pending_fresh_bytes_post_ghost-jobs.json` — "Ghost Jobs Are Everywhere..." (Industry Trends, 1305 words, Sep 8)
- `scripts/pending_fresh_bytes_post_recruiter-ghosting.json` — "Radio Silence: Why Recruiters Ghost You..." (Troubles, 1359 words, Sep 9)

## Agent Relevance

- Scraping agents (resume/job posting collection) → [[Key-Takeaways|Takeaway T-A2]] (autonomous error recovery)
- Tailoring agents → [[10-PROPERTIES/Story-Engine/Objectives#Agent: Novelist|Agent: Novelist]] equivalent (prose generation)

## Compounding Notes

- RoleFresh's scraping retry logic → [[Self-Healing-Pipelines]]
- Anti-deskill protection (user noted) → [[Key-Takeaways|Takeaway T-C3]] from OctoGentic
