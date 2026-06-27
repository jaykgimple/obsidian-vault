---
title: Lesson: Cover Upload Gap
created: 2026-06-27
tags: [lesson, story-engine, media]
status: active
---

# Lesson: Cover Upload Gap

> `_generate_book_cover` returned early if local PNG existed without uploading to Supabase storage.

## What Happened
- Cover PNGs generated locally, sitting in `/covers/`
- `_generate_book_cover` had: `if local_file: return url`
- This skipped `_upload_cover_to_supabase()` entirely
- Result: `cover_image_url` = local path on server, not Supabase storage URL

## Fix Applied
- Always call `_upload_cover_to_supabase()` regardless of local file existence
- Handle 409 (duplicate file) gracefully — still update book record URL
- Self-heal: if book exists in Supabase with empty `cover_image_url`, check for local file → upload
