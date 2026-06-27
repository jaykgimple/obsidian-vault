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
> Part of → [[00-META/Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (Vercel) |
| Backend | Supabase (shared with Story Engine / Fantasy Stack) |
| AI | Resume tailoring, job matching |

## Status

- Live at: rolefresh.vercel.app
- Supabase project: shared "Bookbrary" instance
- Development priority: **paused** (user focusing on OctoGentic + Story Engine)

## Agent Relevance

- Scraping agents (resume/job posting collection) → [[Takeaway T-A2]] (autonomous error recovery)
- Tailoring agents → [[Agent: Novelist]] equivalent (prose generation)

## Compounding Notes

- RoleFresh's scraping retry logic → [[Pattern: Self-Healing Pipelines]]
- Anti-deskill protection (user noted) → [[Takeaway T-C3]] from OctoGentic
