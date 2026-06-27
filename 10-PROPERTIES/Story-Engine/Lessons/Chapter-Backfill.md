---
title: Lesson: Chapter Content Backfill
created: 2026-06-27
tags: [lesson, story-engine, data]
status: active
---

# Lesson: Chapter Content Backfill

> Content lives in `manuscript_chunks`, but Supabase books/chapters are empty until pushed.

## What Happened
- After generation, `chapters.current_words = 0` in Supabase
- Content was in `manuscript_chunks.polished_content` only
- Bookbrary UI showed books with 0 words

## Fix Applied
- `push_series_to_supabase()` backfills chapter content from `manuscript_chunks`
- Aggregates all chapter's chunks → `chapters.content`
- Sums chunk words → `chapters.current_words`
