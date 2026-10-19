# RoleFresh: Fresh Bytes Publish Blocked By Supabase DB Outage

Date: 2026-09-28
**Status: RESOLVED (Oct 2026)** — RoleFresh migrated off Supabase to Neon Postgres. This note is historical; the outage root cause never got a Supabase-side fix and was instead bypassed by migrating.

## What happened
The Fresh Bytes cron (Chief Content Officer) wrote a ready-to-publish post (1258 words, category "Troubles") but could not publish it because the RoleFresh Supabase database is unreachable.

## Root cause diagnosis
- Project: sabexijntgtwflthkzdh (name "jobbox-os", region us-east-1). Postgres 17.
- Project status shows ACTIVE_HEALTHY and the API says "This project is not in a paused state", so this is NOT the free-plan 7-day inactivity pause.
- The database host db.sabexijntgtwflthkzdh.supabase.co resolves ONLY to an IPv6 address (2600:1f18:...), no IPv4 A record.
- Health check: UNHEALTHY, "connect ECONNREFUSED [IPv6]:5432".
- Transaction pooler (aws-1-us-east-1.pooler.supabase.com): "EAUTHQUERY: connection to database not available" (backend Postgres down).
- No platform-wide outage (status.supabase.com shows operational).

## What was tried (all failed)
1. Management API /database/query: initially 429 ThrottlerException, then same ECONNREFUSED.
2. REST API (service role key from .env.vercel): "Invalid API key" (stale/rotated key).
3. Direct pooler via psycopg2 (publish_blog_direct.py): "connection to database not available".
4. Management API /restart endpoint: invoked twice, HTTP 200, no recovery after 10+ min.

## Impact
- Fresh Bytes blog pipeline blocked (post not published today).
- Likely the whole RoleFresh app + job scraper are down for users (same DB).
- This has persisted 24+ hours: yesterday's fresh_bytes_retry.py also logged "db not healthy".

## Recommended action
Open a Supabase support ticket or check the dashboard for this project. The restart API was accepted but did not recover the database node. Verify the service role key in Vercel env is current. Consider upgrading RoleFresh off the free plan to avoid future auto-pause risk (Jay to decide; cost-conscious).

## Post status
Written and staged at /tmp/fresh_bytes_post.json and copied to /root/projects/rolefresh/scripts/pending_fresh_bytes_post_* for retry. Publish pending DB recovery.