---
title: LucentSkill Accessibility Audit
created: 2026-09-18
tags: [lucentskill, accessibility, wcag, audit]
status: active
aliases: [LucentSkill WCAG Audit]
---

# LucentSkill Accessibility (WCAG 2.2 AA) Audit

> Part of → [[LucentSkill]] ← [[Home]]
> Date: 2026-09-18

## Bar
WCAG 2.2 Level AA (current W3C standard). Satisfies EAA (live June 28 2025, EN 301 549), ADA, Section 508.

## Systemic root causes (fix once, propagates)
1. No skip-to-content link (2.4.1) - layout.tsx.
2. No global :focus-visible; inputs use outline-none + faint ring (2.4.7/2.4.13) - globals.css.
3. Pervasive low-contrast text: text-white/40 = 3.76:1, /45 = 4.49:1, /35 = 3.12:1, /30 = 2.58:1, /25 = ~2.2:1. All fail 4.5:1. Minimum for small text = text-white/50 (5.3:1), prefer /60. - EVERYWHERE (1.4.3).
4. No global prefers-reduced-motion (2.3.3); rotating path names auto-rotate with no pause (2.2.2) - globals.css + page.tsx.
5. All modals lack role=dialog/aria-modal/focus-trap/Escape/focus-return (4.1.2/2.1.2).
6. No aria-live on toasts/status/grading results (4.1.3).
7. Form inputs unlabeled (no htmlFor/id), missing autocomplete (3.3.2/1.3.5/1.3.1).
8. Charts role="img" without name / no accessible alternative (1.1.1) - VisualBlock, SurveyQuestionCard.
9. Tables missing th scope (1.3.1) - crosstab, lesson tables.
10. Toggle/selection state not exposed (aria-pressed/checked/selected) (4.1.2).
11. Icon-only buttons use title not aria-label (4.1.2/2.4.4).
12. Color-only meaning: learning-path color picker (H3), readiness banding (H5) (1.4.1).

## Phased plan
- Phase 1 foundations: skip link + focus-visible + reduced-motion + rotating-text fix + contrast sweep. DONE
- Phase 2 interactive: dialog focus management, aria-live toasts, aria-pressed/toggles, icon aria-labels. DONE
- Phase 3 forms+data: labels/autocomplete, table scope, chart names, progressbar semantics, quiz radiogroup, section focus. DONE

## Status (2026-09-18)
All phases shipped + deployed to prod (www.lucentskill.com). Each piece went through separate builder + harsh critic (2 BAR_WINS loops re-fixed). Remaining minor pre-existing nits (not blocking): SortHeader dead color prop, DocsLayout clear button aria-label, roster invite aria-label vs label consistency.

## Verified already-correct
html lang="en", color-scheme dark, landmarks (header/nav/main/footer), page titles, blog subscribe form role=status/alert, Aurora reduced-motion + aria-hidden.

Full per-file audit: see session 20260917_215700_49d93d09 (audit subagent reports).
