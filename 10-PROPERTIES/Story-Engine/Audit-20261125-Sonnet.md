# Story Engine Audit — 2026-11-25 (Sonnet 5.5, two agents)

Two independent Claude Sonnet 5.5 agents audited `/root/projects/story-engine` (head `eed4b33`) read-only. One did the full pipeline; one did consistency root-cause. Line numbers cite files on disk; live SQLite and Supabase were queried.

**Overall verdict (both agents agree):** the architecture is sound and the fact-checker is genuinely fail-closed, but the prose-quality/consistency gates around it are largely dead or fail-open. The big consistency failures are NOT fixed by "a better model" — they are structural: the engine detects contradictions after writing instead of asserting state before writing, gates read keys that don't exist, and regeneration is a blind resample that leaves stale canon behind.

---

## Agent 1 — Full Pipeline Audit (23 findings)

### What is good (keep, don't touch)
- Fact-checker fail-closed contract (`fact_checker.py`, `engine.py:1977-2237`)
- Dual-checker + judge consensus (`engine.py:1968-2052`)
- Deterministic world-state layer with committed-then-applied deltas (`world_state.py`, `engine.py:1613,2054-2081,2431-2460`)
- Gauntlet rewrite is re-verified and reverts if it breaks continuity (`engine.py:2288-2355`)
- Deterministic beat contract / forbidden-move hard block (`engine.py:1680-1760,2391-2406`)
- Cursor reconcile from DB truth (`engine.py:1343`)
- Idempotent schema migration + dedupe (`core/database.py`)
- Boundary dedupe + continuity handoff split-before-truncation
- JSON salvage with `json_repair` + completion nudge
- Supabase integer-id resolution (no uuid leak; no dup books/chapters)
- Config model allowlist (`_validate_model`)
- Em-dash strip on main final-prose paths

### Findings (id, severity/effort, title)
- **F01 critical/S** Dev editor only sees `prose[:3000]` (~500 words); segments average 615-1155 words, so the ending is never judged. (`dev_editor.py:111`)
- **F02 critical/S** Dev-editor thresholds are prompt text only. The JSON schema (`dev_editor.py:82`) has NO `consistency`/`pacing` keys. Engine reads `scores.get('consistency', 10)` → always 10, so the "consistency < 9" revision trigger is dead code. 446/690 segments have quality_score exactly 8.0 (the code default).
- **F03 high/S** Dev-editor failure fails open: exceptions fall through to copy-edit and ship with fabricated score 8 (`engine.py:1877,1947-1948`). After `max_revisions=4` a still-failing segment ships with no post-loop check.
- **F04 high/S** Revision-loop bugs: `revision_notes` set once and never refreshed; forbidden-move/outcome checks dropped on re-review; 0.4x-word acceptance spins; ending-fix path calls `write_segment` with no series ids AND appends `## CONTINUITY` into prose.
- **F05 high/M** Gauntlet failure still ships (357 "did not clear bar" vs 291 pass = 55% fail); default bar is low ("readable, coherent genre fiction"); `_regenerate` bypasses dev-editor + copy-editor; critic exception → "bar" → pointless rewrite; no best-of-draft selection; sequel anchor (`_prior_scene_turn`) missing in gauntlet regen.
- **F06 high/S** Copy editor can silently drop the middle of >6000-char segments (first 3000 + "[... middle section ...]" + last 3000, output replaces whole). No length/sanity guard.
- **F07 medium/S** AI-ism filter inconsistent across 3 lists, `fix_ai_isms` produces broken prose (deletes "meanwhile" leaving ", she ran."), causes infinite regen churn (up to 5 full-pipeline rounds).
- **F08 medium/S** `strip_em_dashes` damages dialogue ("I didn't—" → "I didn't, "), leaves en dashes and " -- ". 184 local / 165 Supabase chapters still contain em dashes.
- **F09 medium/M** POV and tense enforced only by prompt; word count never enforced at generation time.
- **F10 critical/M** A single 429 (rate limit) permanently downgrades the ENTIRE process to a local 9B model, silently, for every agent including the critic and fact-checker judge, for the rest of the run.
- **F11 high/S** Circuit-breaker "skip" logic escalates: after 3 cumulative errors every later error skips another segment.
- **F12 high/M** Beta-reader + QC regeneration leave stale Supabase content and stale embeddings; full book re-push + re-embed per regenerated segment.
- **F13 high/M** Supabase push never checks HTTP responses; status enums leak; partial chapters pushed (Chrono-Compass books "completed" while chapters "generating"; finish series have 0 embeddings).
- **F14 critical/S** Watchdog heartbeat written ONCE at run_all start → "hung" detector kills a healthy engine every 30 min.
- **F15 high/S** Watchdog restarts finished/cancelled series forever; overrides cheap model with paid one.
- **F16 high/S** `run-all` always exits 0 → queue worker marks partial/aborted series "completed" and pushes them.
- **F17 medium/S** queue_worker: `sqlite3.Row.get` crash, name-based identity collisions, 24h blocking run, unencoded URL.
- **F18 medium/M** Schema versioning cosmetic; auto-fix writes goal text as state; NULL-key chapter orphans; status CHECK + enum drift.
- **F19 high/M** `define_series` accepts `segments_per_chapter` 4-8 but architect always emits exactly 4, and engine crashes/loops on mismatch.
- **F20 medium/M** Chapter counsel + beta-reader weaker than documented (counsel is additive-only, discards resolutions; beta-reader has no cross-chapter synthesis despite docstring).
- **F21 medium/M** Throughput/cost: global 10s pause per call, serialized dual checkers, up to ~40 LLM calls per segment.
- **F22 medium/S** Semantic segment embeddings missing for most series + stale on regen (no backfill).
- **F23 low/S** Misc: chapter word-count signal always 0; stale model warning; push/cover run inside open SQLite connection; audit only checks presence not content/embeddings; no tests beyond world_state.

### Priority (Agent 1)
1. F10 (429 sticky downgrade)
2. F01+F02+F03 (dev-editor repair — cheapest high impact)
3. F14+F15+F16 (operational self-healing)
4. F12+F13 (delivery correctness)
5. F11+F19 (cursor + outline)
6. F05+F06+F04 (gate + prose integrity)
7. F07+F08+F09 (prose filters)
8. F17+F18+F20+F21+F22+F23 (hardening)

**Suggested first PR:** F01+F02+F03 (~60 lines), F14 (2 lines), F16 (exit code), F10 part 1 (scope fallback). Then F12/F13 shared supabase_sync module. Then backfills (embeddings, status, em-dash).

---

## Agent 2 — Consistency Root-Cause Audit

### Headline
The guards are a post-hoc stack of weak LLM judges over lossy, non-authoritative context. Four structural defects let violations through:

1. The "authoritative" registry is **derived from the prose afterwards**, not asserted by the writer beforehand; and its time-aware rule treats **every cross-segment change as legal**.
2. **Several gates are dead or fail open.**
3. **Regeneration is not a transaction** — it re-outlines the whole chapter and leaves stale facts + embeddings behind.
4. **Memory is a recency window** (60 facts) + plan summaries, not entity-keyed retrieval of what was actually written.

### Root causes (RC1-RC8)
- **RC1** No single authoritative canon shared by writer and checkers (each reads different lossy slices).
- **RC2** Detect-after-write instead of assert-before-write (state extracted by cheap LLM after prose exists; writer never declares what changed; missed extraction leaves no trace).
- **RC3** Time-aware legality ("later = legal", `world_state.py:389-390`) → only same-segment conflicts are hard; silent cross-segment flips are exactly what's leaking.
- **RC4** Dead + fail-open gates (consistency>=9 reads a key never produced; dev-editor ships after 4 fails; "error" segments count as done; push proceeds on warnings).
- **RC5** Regeneration is a blind resample, not a transactional patch (no prior draft/findings passed; outline overwritten; stale handoff/facts/embeddings).
- **RC6** Memory lossy at continuity's exact fidelity (60-fact recency window; digests are pre-written plan text; judge sees 1500 chars + ~20 facts).
- **RC7** Immutable attributes prompt-only (gender/name/hand-side; 0 of 23 DNA characters across series 6/7/9/10 carry gender).
- **RC8** Judges correlated and under-informed (same prompt/context/model; judge confirmed 0 real issues in 97/99 disagreements; tiny excerpts).

### Permanent fixes (F1-F10)
- **F1** Write-time state-delta contract: novelist asserts PRECONDITIONS + DELTAS (with verbatim quote + event tag); engine validates deterministically before any gate; LLM extractor demoted to recall cross-check. *Kills RC2 + teleport/holder/hand flips at the source.*
- **F2** Redefine registry legality: any holder/location/hand/status change needs a narrated transfer event; immutables (gender, name, hand side, scar) never change; add `as_of()` from history; remove out-of-order exemption (`:346-353`); canonical entity IDs. *Kills RC3.*
- **F3** Canonical bible of immutables + deterministic linters (pronoun-coreference, name-vs-alias, left/right-on-object, geography). *Moves RC7 from probabilistic to deterministic.*
- **F4** Rebuild fact ledger: versioned/superseding/entity-keyed; extract from FINAL shipped text (after gauntlet); pin counsel facts; rolling prose summaries replace plan digests. *Fixes RC6 + the series-7 pollution (55.3 facts/segment).*
- **F5** Transactional regeneration: never delete outline row; stage candidate; pass findings + rejected draft; commit atomically; rollback on fail; mark downstream stale + re-check boundary preconditions only; gauntlet revert also reverts handoff. *Fixes RC5 + divergent/repeated scenes.*
- **F6** Make every gate fail closed: derive consistency deterministically from schema keys that exist; default missing keys to FAIL; refresh revision_notes; block on exhausted revisions; remove "error" from cursor-done; require zero errors + beta-read pass BEFORE push. *Removes all quiet ship paths.*
- **F7** Handoff derived from the registry, not self-reported: render CURRENT STATE from registry as-of prev segment; verify writer's `## CONTINUITY` against it; require immediate predecessor handoff. *Location guard stops trusting unverified text.*
- **F8** Real tier-3 whole-book review: deterministic (replay history, linters, repeated-scene cosine) + LLM, findings fed back to targeted rewrites, re-verified; chunk instead of `[:12000]`.
- **F9** Outline from actual end-state + per-beat pre/postconditions; sequel anchored to shipped ending prose.
- **F10** Stronger independent judging: full segment + entity-keyed facts to the judge; different model from checker B; free-text issue hard iff both cited passages verifiably appear; fix copy-editor middle-drop.

### Priority (Agent 2)
F6 → F3+F4 → F2+F1 → F5 → F7,F10,F8,F9

### Do NOT re-propose (already works / already known dead-ends)
- Grounded verbatim-quote extraction (works).
- Time-aware same-frame contradiction as the ONLY rule (this is WHY flips pass).
- Prompt-only "NO LEFT/RIGHT" without a deterministic enforcer.
- Raising dev-editor threshold higher (gate reads a key that doesn't exist).
- More gauntlet rounds / stricter critic bar (critic is blind to continuity).

### Verification plan
1. Golden regression corpus from real shipped defects (Ural Owl door, Springfield/wrench, card reversal, taped-door timeline, Talen she/her runs, gauntlet left/right flips, divergent escape branches).
2. Behavioural gate tests (mock LLM): dev-editor key defaults to fail, post-max-revision block, error halts cursor, gauntlet revert reverts handoff, regen preserves outline, cross-segment flip rejected.
3. Seeded-fault mutation eval (swap pronoun, change hand, teleport, rename, repeat scene) — target near-100% deterministic recall.
4. Held-out 20-30 chapter consistency eval (new model).
5. Data-hygiene metrics (facts/segment ~15-20, zero dup facts, one entity per object, no gender-less characters, zero error segments).
6. Focused re-run (series 7 Book 1, single writer process) then full run; push only after clean.

---

## Convergence (what to act on)

Both agents independently hit the same four truths:
1. **The consistency>=9 gate is dead** — it reads a JSON key the dev-editor never emits, so it defaults to "pass" and never fires.
2. **Cross-segment flips are legal by design** ("later time = legal" lets any silent change through).
3. **Regeneration is not transactional** — stale facts/embeddings/handoffs accumulate and corrupt what the writer/checkers see.
4. **Fail-open shipping** — gauntlet failures, dev-editor exceptions, "error" segments, and run-all exit 0 all let known-bad prose go out.

**The permanent fix is not "a better model."** It is: writer-asserts-state-before-writing (F1), deterministic rules over a canonical entity-keyed registry (F2/F3/F4), transactional regeneration (F5), and fail-closed gates (F6). Model quality is a real but secondary factor (cited only in the judge-correlation and context-fidelity root causes).

Cheap wins (a day or two) that remove the three biggest silent-fail paths: **F6 + F01/F02/F03 (dead dev-editor gate) + F14/F16 (watchdog heartbeat + exit codes)**. Then the structural F1/F2/F4 work.
