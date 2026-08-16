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
- Supabase project: shared "Bookbrary" instance
- Development priority: **paused** (user focusing on OctoGentic + Story Engine)

## Agent Relevance

- Scraping agents (resume/job posting collection) → [[Key-Takeaways|Takeaway T-A2]] (autonomous error recovery)
- Tailoring agents → [[Story-Engine/Objectives#Agent: Novelist|Agent: Novelist]] equivalent (prose generation)

## Compounding Notes

- RoleFresh's scraping retry logic → [[Self-Healing-Pipelines]]
- Anti-deskill protection (user noted) → [[Key-Takeaways|Takeaway T-C3]] from OctoGentic
