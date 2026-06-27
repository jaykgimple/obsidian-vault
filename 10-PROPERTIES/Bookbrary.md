---
title: Bookbrary — Reader-Facing Platform
created: 2026-06-27
tags: [property, bookbrary, frontend]
status: active
aliases: [Bookbrary Platform, Book Library]
---

# Bookbrary

> Reader-facing web platform for consuming generated book content.
> Repository: `/root/projects/bookbrary`
> Part of → [[00-META/Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (Vercel) |
| Backend | Supabase (auth, storage, database) |
| Data | Supabase PostgreSQL + Storage (covers) |
| Integration | Story Engine pushes via `push_series_to_supabase()` |

## Data Model

- `books` table: book metadata (title, cover_image_url, series_id, words)
- `chapters` table: chapter content (content, current_words, order)
- Storage: `book-covers` bucket for cover images

## Integration Points

| From | To | Mechanism |
|------|-----|-----------|
| Story Engine | Supabase `books`/`chapters` | Direct push via `push_series_to_supabase()` |
| Bookbrary UI | Supabase | Reads via anon key + RLS |
| User submits series | Supabase `generation_queue` | Frontend inserts `status: "pending"` |

## Key Flows

1. **Generation**: User submits → queue item → Story Engine picks up → generates → pushes
2. **Consumption**: User browses → reads chapters → Bookbrary UI renders markdown
3. **Review**: → [[Pattern: Review-and-Revision]] → updates Supabase chapters

## Agent Relevance

- → [[Agent: Pipeline Orchestrator]] pushes to Bookbrary's Supabase
- → [[Agent: Cover Artist]] generates covers in Supabase storage

## Compounding Notes

- Reader feedback (if tracked) could feed back into → [[Pattern: Coherence-Scoring]]
- Bookbrary's `processing` status display → [[Takeaway 7.5]] from OctoGentic (show the agent's work)
