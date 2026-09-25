# Course-Generation Failure Fix (visual union + correct-index drift)

**Date:** 2026-09-24
**Property:** LucentSkill
**Commit:** 603d9ab · deployed READY (dpl_AxcHKwkF)

## Symptom
Intermittent course generation hard-failures showing `Prism returned invalid structure: sections.N.visual: Invalid input` (all sections) or `sections.0.questions.0.correct: Too small`.

## Root cause (two near-miss defect classes from deepseek-v3.2)
1. `sections[*].visual` is a 3-way Zod union (chart | diagram | legacy-SVG). When a visual fails all three members (unknown `chartType`, diagram `edge` referencing an unknown node id, node `kind` outside enum), Zod collapses to a single opaque `invalid_union` whose top-level message is literally `Invalid input`. The old `prism.ts` issue mapper only recorded `i.message`, discarding the nested errors, so the repair loop re-fed the model a useless error and it re-emitted the same bad shape.
2. `questions[*].correct` is `.int().min(0).max(5)`. The model intermittently emits `-1`, a numeric string, a float, or an out-of-range index; the section preprocess only checked `typeof correct === "number"`, so bad values reached strict Zod and failed `.min(0)`.

## Fix (deterministic repair at the coercion layer)
- `prism.ts`: surface `invalid_union` sub-errors. Note: repo runs **Zod 4.4.3** where the nested issues live in `i.errors` (2D array), NOT Zod 3's `unionErrors`.
- `courseStudio.ts` `normalizeCourseShape`: (a) clamp `questions[*].correct` to `[0, options.length-1]`; (b) drop a `visual` that fails `VisualSchema.safeParse` (leaving valid visuals byte-for-byte intact), relying on the non-blocking `planVisuals` fill-gap pass to backfill.
- `schemas.ts`: new `coerceQuestionCorrectIndex(value, optionCount)` helper beside `coerceExercisePoints`/`coerceChartValue`.
- Strict section-regeneration schema (`LessonSectionShapeSchema`) deliberately left untouched so a bad visual/questions there still fails and triggers the repair loop.

## Verification
- `tsc --noEmit` exit 0, 201/201 tests pass (new `src/lib/courseValidate.test.ts`).

## Lesson
- Zod 4 renamed `unionErrors` to `i.errors` on `invalid_union` issues. Grep the installed zod major version before writing issue-mapper code; a Zod-3-grammar patch compiles and tests green but silently prints no detail.
- Deterministic near-miss repair belongs in the Prism `normalize` coercion (BEFORE Zod validation), matching how exercise points and chart values were already handled. Dropping a malformed optional `visual` is safe because `planVisuals` is additive + non-blocking (`generationWorker.ts` catches a planner failure and persists the course as-is).