---
title: LucentSkill — Team-Scoped Content + Delegated Lead
created: 2026-08-30
tags: [lucentskill, feature, teams, permissions, gauntlet]
status: active
aliases: [Teams Feature, Team Lead Role]
---

# Team-Scoped Content + Delegated Lead

> Goal: let a non-admin team lead author/publish courses scoped ONLY to their own team.
> Bar: WorkRamp Groups + folder-level delegated roles (see `.agents/gauntlet-bar.md` in repo).
> Part of → [[LucentSkill]]

## Why

Matt (business partner) asked: "can courses be allocated to unique teams? e.g. a Data Governance lead creates courses specific for his team." Verified against schema: today courses are org-wide (only track + engagement-tier scoped), authoring is admin-only, and "team" is a free-text roster department, not a first-class entity.

## Scope (4 pieces, gauntlet loop)

1. **Team data model** — migration `012_teams.sql`: `teams` + `team_members` (membership-scoped lead role) + `dynamic_courses.team_id` (NULL = org-wide).
2. **Course→team visibility** — filter team-scoped courses in `dynamicTree.buildTree()` so they only merge into that team's path.
3. **Team-lead permission tier** — scoped authorization (lead can author/publish for their team only), NOT a global `users.role` change.
4. **Admin UI** — create team, assign lead/members, pin course to team.

## Decisions

- Lead role lives on `team_members.role` (lead | member), not `users.role` — a user can lead one team, be a member elsewhere.
- Tenant isolation enforced at SCHEMA level via composite FKs `(org_id, id)` on every cross-table reference. Round-1 critic caught that a prose-only claim was insufficient.
- Dropped the 6-tier WorkRamp "waterfall" (Admin/Full Editor/Limited Editor/Edit/Assign/Read) — too heavy for the ask; lead/member is the right granularity.
- `dynamic_courses.team_id` is `ON DELETE CASCADE` (scoped content dies with its team; RESTRICT would break org cascade).

## Status

Piece 1 (migration) through 2 critic rounds; final ordering bug (users composite-unique index must precede the `teams` table) found by executing against a scratch DB, not the critic. Pieces 2-4 pending.

## Lessons

- A harsh critic finds schema-level gaps (missing composite FKs) that a careful builder asserts in comments but never enforces. Execute the migration against a scratch DB before trusting "it's idempotent."
