---
type: note
tags: [rolefresh, qc, feedback, triage, resume-parser]
created: 2026-11-24
---

# RoleFresh QC Feedback — Assessment + Resolution (2026-11-24)

43 feedback items triaged. Shipped commit `873ef2f`, deployed to rolefresh.vercel.app
(verified live via CSP `frame-src … blob:` header appearing). Verified `npx tsc --noEmit` clean
and 983 vitest tests pass (only the known pre-existing rewrite-summary note-assertion fails,
documented in the rolefresh-development skill; do NOT chase it).

Final disposition: 31 resolved, 7 reviewed, 5 open (parked).

## Root cause of the critical "everything lands in Location" bug

`parseResumeToSections` processed text line-by-line, but PDF/DOCX extraction glued section
headers onto adjacent content ("Amarillo TX • • SUMMARY", "…efficiently. EXPERIENCE Pak A Sak",
"- operations. EDUCATION"). No header was detected, so the whole document became the `header`
section and `extractContact` dumped everything-after-name into `location` — and the structured
fields (summary/experience/education/skills) came back empty. Confirmed against AJ Goetz's real
stored `rawText` in Neon.

## What was fixed (commit 873ef2f)

- **Parser (root cause):** `normalizeSectionHeaders` rewritten to un-glue headers via bullet
  separators, sentence punctuation, and glued trailing content; now called inside
  `parseResumeToSections` so upload/parse/save/score/export ALL benefit. Added
  "business & academic projects" etc. to the projects vocabulary. Re-wrote `parseEducation`
  for the pipe-separated school-first two-line shape + GPA skip. Regression test added to
  tests/structured-resume.test.ts.
- **View/Print + export:** CSP `frame-src` gained `blob:` (blank preview fix); `generatePDF`/
  `generateDOCX` normalize headers and render header-less prose (cover letter) as body text, not
  a 3-line contact header.
- **FreshApply:** on-demand `scripting.executeScript` injection (activeTab) + `<title>`/description
  fallback + double-injection guard. Rebuilt the extension zip.
- **JD scrape:** auth-wall detection → clear "requires login, paste the JD" message instead of
  storing nav junk.
- **QC widget:** wider modal + annotator; per-annotation select/move/delete; image-load redraw
  (blank viewer fix).
- **Pipeline modals** widened; **education entries reorderable**; **resume rename + Set Current**
  (PATCH `name` / `makeDefault`); fixed the broken picker score/word display (was reading
  `ats_score`/`content` that the API never returns).

## Follow-up (commit 55a91f1) — all 5 parked items built, shipped, verified

- **Draft/Publish** — `ResumeVersion.status` (draft|published, default published so no
  regression; download stays free/ungated) + dashboard status pill, Publish/Make-draft toggle,
  picker badge. Also fixed the broken "Set Current" switch (`makeDefault` on PATCH).
- **Feedback threads + badge** — `FeedbackReply` model, admin reply UI (panel), user "My
  feedback" view + red unread badge on the widget (`GET/POST /api/feedback/mine{/read}`).
- **Feedback attachments** — QC form file attach (image/doc, ≤3), stored on `Feedback.attachments`,
  rendered/downloadable in the admin panel.
- **Bullet continuation merge** — a lowercase dash-marked line after an open bullet merges into it
  (no more "last words in their own box"); leading "●" glyph stripped.
- **Bold-in-preview** — `stripMarkdownEmphasis` strips `**`/`__`/`*` so intake-derived rewrite
  output no longer renders bold.

Deployed to rolefresh.vercel.app (verified live via `/api/feedback/mine` → 401). tsc clean,
build clean, 991 vitest tests pass (2 dashboard/editor .tsx tests are flaky under full-suite
parallel load but pass in isolation; the one rewrite-summary note assertion is the known
pre-existing failure). Final feedback disposition: **36 resolved, 7 reviewed, 0 open.**
