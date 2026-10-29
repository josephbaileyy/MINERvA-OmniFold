# Register retrospective: what moved the PRD raters, paper rounds r8–r20 and the note's rounds (2026-10-28)

**Under:** `DECISION-20261028-joseph-protections-n4-release-retrospective.md` item 4 (`:40-41`): "which operations moved
the pairwise and P1. It is read-only analysis. DSPy prompt optimization is not set up now."

**Written by** a read-only research agent for the director, on a detached worktree of origin/main `371cccecb`. No rater,
model, CLI or compute job was run. The director reviewed it and committed it.

**MEASURES:** nothing. Every score, count and word figure is transcribed from a committed record and cited to its
line. The only new numbers are this record's tallies of committed rater outputs (§3), and each tally names its files.

**CITABLE FOR:**
- what each register round changed and how the raters scored it, as the round records state;
- the classification of the passages that sol/sol2 quoted under P1 (§3), with its stated rules and borderline cases;
- the operation-by-operation record (§2) and the options with their evidence (§5).

**NOT CITABLE FOR:**
- any physics claim;
- a recommendation: §5 lists options, and Joseph decides;
- rater behaviour on other documents, or on prompts other than P0, P1, P1N, P2 and P2N;
- run-level quote counts for r15–r18 beyond what their REPORTs state (their raw rater outputs are not committed, §7).

**Paths.** Relative to `docs/orchestration/state/2d-closeout/stageF/methods/` unless they begin `DECISION-` (in
`docs/orchestration/`). "MI" is `METHODS-IMPLEMENTATION.md`. "sol" is gpt-6.1-sol through codex-school; "sol2" is the
same model through codex-school2 (`register-method/HANDOFF.md:36-38`).

---

## 0. In brief

- **P1 with sol/sol2 has not moved since r11.** Every one of the 39 committed or recorded P1 runs on the paper from r11
  to r20, over 13 versions, is 3 (§1.1). The only measured P1 rise is 2.50 → 3.00, from the r8 text to r11, across
  register loop 1 (`rater-calibration/REPORT.md:74,76,107`; §6 item 5).
- **The pairwise comparison did move, and it moved most for whole-text restructuring.**
  - The three rounds that rewrote the whole paper from an outline (r12, r17, r19) won 5 of their 6 sol runs at
    strength 2.
  - The four rounds that reworded named passages in place (r13, r14, r16, r20) won 1 of their 8 sol runs at strength
    2 (r14's two went to the old version), and two of the four were not adopted (§2).
- **On the note, moving the records out was the only operation that moved P1N beyond noise.** Batches n1–n3 moved the
  sol2 mean by +0.05 in total, against a measured noise SD of 0.22 per piece (§1.2, §2).
- **The quoted passages are mostly protected or guardrail text.** Of the 54 quotes in the committed sol/sol2 P1 files:
  - 27 are in text a Joseph decision requires or protects;
  - 24 are disclosures or qualifiers the guardrail keeps;
  - 3 are ordinary prose (§3).
- **Removing a quoted passage never raised P1.** Five passages left the paper; each stopped being quoted, and the three
  quote slots refilled. The Data availability text came back into the quotes at r18 with byte-identical source (§3.3).
- **Repeatable and backfired** (§4):
  - repeatable: moving records and histories to the companion; rewriting from a reverse outline with a fact ledger;
    one home per caveat; splitting overloaded sentences with care;
  - backfired: rewording quoted passages in place (r14, r20); mechanical splitting (§11 in n2); full rewrites of
    short, sequential text (App. A in n1).
- **Three records disagree with their raw rater files** (§6).

---

## 1. Round by round

### 1.1 The methods paper

r8–r11 were scored with the six-question register prompt P0, one run per model; from r12 on, with P1 (three runs) and
P2 (both orders, both models) (`rater-calibration/REPORT.md:59-63,103-116`). "s" is the P2 strength (1 slight, 2 clear,
3 strong; `rater-calibration/prompts/P2.prompt.txt:9`).

| round | base → new | operations | words before → after | P2: NEW wins of 4; sol/sol2 s; Gemini s; flips | P1 sol/sol2 before → after | P1 Gemini before → after | adopted | passages sol/sol2 quoted (runs) |
|---|---|---|---|---|---|---|---|---|
| X4–X7 | pass-2 text, drafts 3–7 | outside-referee rounds on framing and claims (MI:72-84) | not recorded | not run (verdicts "major revision") | not a register score | not a register score | n/a | not recorded |
| r9 (loop 1, round 1) | r8 `e5ae5b11` → `mrg1` | section rename and fold; scope consolidated into Sec. I; audit phrasing as criterion, value, outcome; abstract simplified; AI acknowledgment condensed (MI:267-276) | not recorded; abstract about 149 (MI:273) | not run | P0: 3 → 3 (MI:264,283) | P0: 3.5 → 3.5 (MI:265,284) | stop rule met (MI:312) | not recorded |
| r10 (round 2) | → `mrg9` | structural reorder from a reverse outline: Table I of findings, new Sec. VI, Sec. VII condensed, bookkeeping to the note; D-ID addition (MI:339-357) | not recorded | not run | P0: 3 → 3.5 (MI:386) | P0: 3.5 → 3.5 (MI:387) | yes | not recorded |
| r11 (round 3) | → `mrg16` | abstract shortened; one scope paragraph; process vocabulary replaced ("gate" → "acceptance threshold"); two sol rewrites adopted; plain captions (MI:412-424) | abstract 149 → 135 (MI:413) | not run | P0: 3.5 → 3 (MI:451) | P0: 3.5 → 3.5 (MI:452) | yes, on review (MI:458-459) | not recorded; sol's first example was its own r10 rewrite (MI:456-457) |
| calibration | ours-old (the r8 text; §6) vs r11 `2f55cd53` | (the whole of loop 1) | r11: 9,844 blinded (`rater-calibration/REPORT.md:41-42`) | current wins 4 of 4 (`:83`) | P1: 2.50 → 3.00, z ≈ 5 (`:74,76,107`) | P1: 2.50 → 2.17 (`:74,76`) | n/a | not recorded |
| r12 | r11 → `5f717bf4` | fresh writer; every section rewritten from a reverse outline and a 341-row fact ledger; chronology and bookkeeping to the note; one scope paragraph; Table III added (MI:497-528) | printed prose 7,535 → 6,558 (MI:513) | 4; sol 2, 2; Gemini 3, 2; none (MI:584) | 3,3,3 → 3,3,3 (MI:582-583) | 2.17 → 2.50 (MI:582-583) | yes (MI:586) | VII C design and budget 3/3; Data availability 3/3; VII E hydrocarbon 2/3; IV B rebuilt band 1/3 (`r12/scores/P1__r12__sol__r{1,2,3}.txt`) |
| r13 | r12 → r13 | fresh writer on the 47 P3-flagged sentences (4 moved to the note, 27 restated as design fact or scope, 9 left, 7 protected); the three always-quoted passages rewritten; 7 long sentences split (MI:599-608) | not recorded | 4; sol 1, 2; Gemini 2, 2; none (MI:630) | 3,3,3 (sol2 on r12: 3,3) → 3,3,3 (MI:629,645) | 2.50 → 2.67 (MI:629) | yes (MI:632) | Data availability 3/3; VI binned diagnostic 3/3; VII C lost pseudo-experiments 2/3; design 1/3 (`r13/scores/P1__r13__sol__r*.txt`) |
| DA shortening (PR #212) | r13 → `4ba0dd2f` | Joseph's Data availability text cut from about 262 to about 140 words, facts to the note (`DECISION-20261021-joseph-da-and-note-records.md:9-11,33-43`) | about 262 → about 140 (DA only) | not run | 3,3,3 → 3,3,3 (MI:736,749-750) | → 2.5,2.5,2.5 (MI:736) | yes (Joseph) | on `4ba0dd2f`: lost pseudo-experiments 3/3; hydrocarbon 3/3; five-iteration rule 2/3; scope 1/3 (`r14/scores/P1__m__sol2__r*.txt`) |
| r14 | `4ba0dd2f` → `ed117866` | "scope inside the claim": each flagged caveat restated with its scope as subject or opening; lost-pseudo-experiment counts and binned-diagnostic exclusions moved to the note (MI:721-725) | not recorded | 1; sol2 OLD 1, OLD 1; Gemini OLD 2, NEW 2 (position bias) (MI:738-741) | 3,3,3 → 3,3,3 (MI:736-737) | 2.5 → 2, 2.5, 2.5 (MI:736-737) | **no** (MI:742-744) | hydrocarbon 3/3; five-iteration 1/3; IV B rebuilt band, seed pair, budget, reviewers' look, Gaussian-fit diagnosis 1/3 each (`r14/scores/P1__r14__sol2__r*.txt`) |
| r15 | `177bf84b` → `c10f178c` | PRD-study rules R1–R10: positive scope paragraph; new numbered Limitations subsection; Table I limitation column and repeated limitations removed; note pointers 40 → 25; NuWro out of the abstract (`r15/REPORT.md:19-48`) | 6,863 → 6,603; abstract 135 → 115 (`r15/REPORT.md:48`) | 4; strengths 2, 1, 2, 2 (model mapping not recorded); none (`:98-99`) | 3.0 → 3,3,3 (`:105`) | not recorded | yes | five passages, run counts not recorded: rerun pseudo-experiments; "descriptive … do not re-grade"; five-iteration rule; seed panels; budget extension (`:107-113`) |
| r16 | `927f40bf` → `6c4091be` | the five r15-quoted passages reworded in place; a non-sequitur dropped; one sentence split (`r16/REPORT.md:9-24`) | 6,603 → 6,609 (`r16/density.md:18`) | 4; sol2 1, 1; Gemini 2, 2; none (`r16/REPORT.md:39-46`) | 3,3,3 → 3,3,3 (`:53`) | not recorded | yes | run counts not recorded: IV B post hoc rescoring; budget extension; design fixed before the statistic; "is being moved to the refined estimator" (`:53-58`) |
| r17 | `f0b26234` → `63f1d61b` | paragraph-level restructure in four batches from reverse outlines: moves S1–S14, splits, reorders; mean sentence length 25.8 → 20.9 (b2) and 27.1 → 20.5 (b3) (`r17/REPORT.md:16-41`) | rater copy 9,192 → 9,297 (`:41`) | 4; sol2 2, 2; Gemini 2, 3; none (`:114-119`) | 3,3,3 → 3,3,3 (`:131`) | 2.5, 3, 2.5 → 2.5, 2.5, 2.5 (`:132`) | yes (`:159-162`) | VII C design and budget 3/3; IV B post hoc rescoring 3/3; VII E "descriptive … stand" 2/3; III configuration paragraph 1/3 (`:140-146`) |
| r18 | `e270db89` → r18 | history passages to the note (IV B bands; VII C mechanics); nine-item Limitations list folded into the text; scope stated once; process vocabulary removed (`r18/REPORT.md:20-31`) | rater copy 9,348 → 9,221 (`:38`) | 4; sol2 1, 1; Gemini 2, 2; none (`:142-147`) | 3,3,3 → 3,3,3 (`:160`) | 2.5,2.5,2.5 → 2.5,2.5,2.5 (`:161`) | yes (`:176-179`) | III configuration (f) lines 3/3; VII C design and budget 2/3; Data availability 2/3; V D covariance 1/3 (`:167-172`) |
| 5D integration and configuration move (#413) | r18 → `00428d10` | content added (the sixteen-cell result, the measurement framing); non-final configurations moved to the note (`fived16/HANDOFF.md:46-65`) | 9,221 → 10,381 (`r18/REPORT.md:38`; `r19/REPORT.md:43`) | not run | → 3,3,3 (`r19/REPORT.md:107-109`) | not recorded | yes (decisions) | not recorded separately |
| r19 | `00428d10` → `a1702535` | measurement-paper order (variant B): 8 → 6 sections, 14 → 11 pages; calibrated hybrid-null tests, binned-diagnostic detail, Table III, Fig. 4 and O2, O3, O5, O6 to the note; Table I folded into the text; result table added (`r19/REPORT.md:22-41`) | blinded 10,381 → 7,404 (`:43`) | 4; sol2 2, 1; Gemini 2, 2; none (`:92-97`) | 3,3,3 → 3,3,3 (`:109`) | not recorded | yes (`:117-120`) | five-iteration 2/3; Data availability 2/3; Limitations lead, scope, binned diagnostic, listing rule and "the note's calibrated tests" 1/3 each (`r19/measure/P1__r*__sol2.txt`; §6) |
| r20 | `a1702535` → `7ec31a5d` | the six r19-quoted passages reworded, with no structural change (`r20/REPORT.md:7-8`) | 7,404 → 7,395 (`:17-18`) | 2; sol2 NEW 1, 1; Gemini OLD 2, 2; none (`:20-27`) | 3,3,3 → 3 (1 run; `:31`) | not run | **no**; text returned to r19's (`:28,44`) | scope; five-iteration; Data availability (`r20/measure/P1__r1__sol2.txt`) |
<!-- absence-ok: "not recorded" and "not run" cells describe the cited round records only; not claims about results elsewhere -->

**Counting the P1 runs.** That is 36 runs (3 each on r11, r12, r13, `4ba0dd2f`, r14, r15, r16, r17's base, r17, r18,
r19's base and r19), plus sol2's 2 runs on r12 (MI:645) and r20's 1 run. In total: 39 runs on 13 versions, all 3.

### 1.2 The analysis note

P1N is P1 with a chapter framing, rated on blinded pieces of 2,000–8,000 words; P2N is P2 with the same framing
(`rater-calibration/NOTE-BASELINE.md:9-14`; `register-method/HANDOFF.md:74-76`). Means are over pieces.

| round | base → new | operations | words | P2N | P1N sol/sol2 mean | P1N Gemini mean | adopted | what the raters named |
|---|---|---|---|---|---|---|---|---|
| baseline (10-21) | r12 build, 136 pp | — | 60,963 in 15 pieces (`NOTE-BASELINE.md:7-8`) | — | 2.83; anchors 3.875 (`:24-26`) | 2.30; anchors 3.375 (`:24-26`) | — | 135 quotes: BOOK 42, HEDGE 38, JARG 34, HIST 33, CODE 23, META 22, PROC 22, DENSE 13 (`:43-55`) |
| glossary g0 | → | one vocabulary: 192 edits in 19 files; status terms reworded; about 20 project terms cleared (MI:676-686) | not recorded | not run separately | not run separately | not run separately | yes | — |
| records move | → `e05c78c7` | Apps. G and J, and the record parts of H and I, to a separate internal document; 82 citations replace 87 pointers (MI:780-791) | pages 138 → 119 (MI:823) | not run separately | not run separately | not run separately | yes (Joseph) | — |
| chapter batches b3–b8, bhi | → `717ecf8b` | a fresh writer per chapter, with reverse outline, ledger and review (MI:860-877) | §§6–8 10,054 → 10,305 (`note-b6/REVIEW.md:202`); §10 5,934 → 5,893 (`note-b7/REVIEW.md:137`); others not recorded | after all of the above, against the baseline: 48 of 48; sol2 s 2 in 22 of 24 runs (`note-rating/P2N-pairwise-analyze.txt:2-29`) | 2.83 → 3.04; body 2.98 → 3.08 (drift +0.06); appendices like-for-like 2.62 → 2.94 (`note-rating/P1N-rerating-compare.txt:18-31`) | 2.30 → 2.46 (`:31`) | yes | records citations in 31 of 126 quotes (MI:914-915); sol2 3.0 in 24 of 28 runs (MI:913) |
| thinning | → `9c10f6c1` | records citations 71 → 19 (MI:930) | not recorded | not run (Joseph stopped model scoring; `DECISION-20261022-joseph-note-records-refs-and-stop.md:27-34`) | not run | not run | yes | — |
| n1 (10-26) | `5bb5e179` → n1 | caveat-study R-N1–R-N7 and R1–R10: histories to one home; one "Principal limitations" paragraph in the ES and §12; one Scope paragraph; process words (`note-n1/REPORT.md:48-55`) | round files 35,997 → 35,349; ES 1,532 → 1,034 (`:61-74`) | 11 of 12 pieces adopted; App. A (N11) 1 of 4 (`:107-120`) | 3.083 → 3.117 (`:167`) | 2.467 → 2.300 (`:168`) | 11 of 12 | Gemini: "laboratory-notebook register", "software audit" (`:172-178`); N11: the base App. A is "shorter and sequential" (`:125`) |
| n2 | `be045af4` → n2 | R-N2a sentence splits ("one claim per sentence", `sec_summary.tex:5`); R-N2b provenance to the records; R-N2e App. A at six quoted passages; records cited by entry number (`note-n2/REPORT.md:73-80`) | round files 43,441 → 43,924, of which app_provenance +265 (`:95-113`) | 12 of 13 preferred NEW; §11 0 of 4 (`:124-138`) | 3.117 → 3.133 (`:168`) | 2.300 → 2.400 (`:168`) | 11 of 13 (§11 failed P2N; App. B/C failed P1N at −0.25) (`:12-16`) | §11: the splits are "choppy and repetitive" (`:144`); App. B/C: "production bookkeeping, development history, repeated scope disclaimers" (`:171`) |
| n3 (10-27) | `0d919b1a` → n3 | R-N3a status, not chronology; R-N3b one home per scope statement; R-N3c list sentences instead of second splits; R-N3d provenance (`note-n3/outline.md:36-58`) | not recorded | 9 of 12 preferred NEW; ES/§1 1 of 4, §12 1 of 4, §8 2 of 4 (`note-n3/REPORT.md:101-114`) | 3.133 → 3.133 (`:137`) | 2.367 → 2.433 (`:137`) | 7 of 12 (`:21-23`) | sol2's 69 distinct quotes on n2's text: stacked qualification 38, history 28, provenance 20 (`note-n3/outline.md:24-32`) |
| consolidation (content PR) | `602ab31f` → | 43 of 60 restatements replaced by pointers to one home; 13 kept by the guardrail, 4 by ruling (`note-consolidate/REPORT.md:26-58`) | TeX 48,904 → 48,384; blinded 52,558 → 52,045 (`:151-152`) | not run (`:5`) | not run | not run | yes | — |
| n4 | — | front-matter restructure, decided (`DECISION-20261028-joseph-protections-n4-release-retrospective.md:30-36`) | — | not yet run | — | — | — | — |
<!-- absence-ok: "not recorded" and "not run" cells describe the cited round records only; not claims about results elsewhere -->

---

## 2. What moved what

The pairwise result is a 3-level preference, and P1 moves in half points. Most cells below rest on 1–3 rounds. Read the
patterns as consistent, not as measured effects.

| operation | rounds where it was the main operation | pairwise record | P1 / P1N record |
|---|---|---|---|
| **Whole-text rewrite from a reverse outline and a fact ledger** (structure, order and sentences together) | paper r12, r17, r19; note b-batches | r12, r17 and r19 each 4/4, sol s 2, 2 / 2, 2 / 2, 1; note before/after 48/48, with sol2 s 2 in 22 of 24 runs | paper 3 → 3 in all three; note body 2.98 → 3.08, within the +0.06 drift |
| **Move to the companion or the records** (histories, bookkeeping, procedure) | paper r10, r12, r18, r19; DA shortening; note records move, thinning, R-N2b, R-N3d | won wherever scored (r12, r18, r19 4/4); not scored alone on the note | note appendices like-for-like 2.62 → 2.94, "most of the like-for-like gain" (MI:911-912); paper P1 unchanged; each moved passage left the quotes (§3.3) |
| **Reword named passages in place** | paper r13, r16, r20; note R-N2e | r13 4/4 (s 1, 2); r16 4/4 (s 1, 1); r20 2/4, not adopted; App. A at six passages 4/4, after the full rewrite lost 1/4 | paper 3 → 3; the reworded passages were often quoted again (§3.3) |
| **Scope inside each claim** | paper r14 | 1/4, not adopted | 3 → 3 |
| **One home per caveat; one scope paragraph; limitations collected or folded** | paper r11, r15, r18; note n1 (summaries), n3 R-N3b, consolidation | r15 4/4; r18 4/4 (s 1, 1); n1 ES/§12 4/4 each; n3 ES/§1 and §12 1/4 each | paper 3 → 3; n1 ES 1,532 → 1,034 words with P1N N01 3, 3 → 3, 3 (`note-n1/REPORT.md:61,147`) |
| **Split overloaded sentences** (R10, R-N2a, R-N3c) | paper r13 (7 sentences), r17; note n2, n3 | r17 4/4; n2 §11 0/4, "choppy and repetitive"; prd-read Q3: three sentences beat one in 24 of 24 (`fived16/prd-read/REPORT.md:43-47`) | no measured P1 effect; R-N2a raised the counted caveats per 1,000 words (`note-n2/REPORT.md:192-199`) |
| **Cut and shorten** | paper r12 (−977 prose words), DA (262 → 140), r19 (−2,977 blinded); note consolidation (−520) | won where scored | paper 3 → 3 at every length from 10,381 to 7,404 blinded words |
| **Vocabulary and glossary** | paper r11; note g0, n1-F | inside winning rounds; not isolated | not isolated |
| **Abstract** | paper r9, r11, r15 | inside winning rounds | not isolated; the abstract is Joseph's text (`DECISION-20261025-joseph-register-rounds-paper-rewrite.md:65`) |

**What the table supports:**
- **The pairwise prefers the larger edit.** The rounds that rebuilt the whole text drew clear preferences (s 2). The
  rounds that touched named passages drew slight ones (s 1), or lost.
  - **Paper.** For r12, r17 and r19, NEW won 5 of 6 sol runs at s 2. For r13, r14, r16 and r20 it won 1 of 8 at s 2,
    and r14's two sol2 runs went to the old version.
  - **Note.** sol2 gave s 2 in 22 of 24 runs on the before/after of the whole register pass. In n1–n3 it gave s 2 only
    on summary pieces: n1 N01 once and N10b twice; n2 N01 twice, N09 once and N10b twice. n3 drew s 1 throughout
    (`note-n1/REPORT.md:109-120`; `note-n2/REPORT.md:126-138`; `note-n3/REPORT.md:103-114`).
- **The pairwise also rewards polish.** The calibration found that its reasons are surface mechanics, and that it
  preferred our paper to the published anchors (`rater-calibration/REPORT.md:84-90`). Gemini's r20 reasons are of that
  kind: numerals, the serial comma, "so it keeps five" (`r20/REPORT.md:33-38`).
- **P1 did not resolve any operation after r11.**
  - On the note, sol2 scored 32 changed pieces in n1–n3, each either adopted or tested. 25 did not move, 4 rose (+0.25
    three times, +0.5 once) and 3 fell by 0.25 (`note-n1/REPORT.md:147-161`; `note-n2/REPORT.md:152-166`;
    `note-n3/REPORT.md:126-134`).
  - Unchanged pieces drift with an SD of 0.22, by up to 0.25 (`note-n2/REPORT.md:266`). The changed pieces' moves lie
    inside that drift.
- **Gemini's P1 moved where sol's did not, in both directions.** On the paper it rose 0.33 at r12 and 0.17 at r13, then
  fell to 2.33 at r14. On the note it fell 0.17 at n1. Gemini does not gate (`rater-calibration/REPORT.md:108`).

---

## 3. The P1 plateau

### 3.1 What the instrument asks for

- **The rubric's level 3** is "stacked qualifiers or defensive hedging, project-internal labels or jargon,
  development-history or procedural narrative, sentences a referee would ask to simplify". Level 4 allows "some
  redundant qualifiers" (`rater-calibration/prompts/P1.prompt.txt:7-8`).
- **Every reply must quote three passages** (`P1.prompt.txt:15-21`). The quote list is therefore a ranking of the three
  worst passages, and it cannot come back empty whatever the text.
- **The justifications restate level 3:**
  - r17: "repeated qualifications, internal bookkeeping, and accounts of analysis development" (`r17/REPORT.md:138-139`);
  - r18: "repeated qualifications, configuration bookkeeping, and development-history passages" (`r18/REPORT.md:165-166`);
  - r20: "repeated qualifications, internal estimator labels, and development and release bookkeeping"
    (`r20/measure/P1__r1__sol2.txt:2`).
- **The measured density stays outside the published range.**
  - After r16 the strict index is 12.3 per 1,000 words, against a corpus median of 2.6 [1.3, 4.2]
    (`r16/density.md:18-31`).
  - The caveat study finds 10.0 distinct caveats per 1,000 words, against 1.4–4.5, and says a register round cannot
    close that gap (`caveat-study/REPORT.md:311`).

### 3.2 Every quoted passage, classified

**Rules:**
- **(a)** The passage is there because a Joseph decision requires or protects it.
- **(b)** It is a disclosure or qualifier the guardrail keeps: a KEEP item, or one an independent review restored for
  accuracy. Its wording can change; its content cannot leave.
- **(c)** Ordinary prose the lane could have cut or recast without a decision.

A passage is classed by its content, not by the rater's complaint about its phrasing.

**Population.** The 54 quotes in the 18 committed sol/sol2 P1 files (r12 ×3, sol2 on r12 ×2, r13 ×3, `4ba0dd2f` ×3,
r14 ×3, r19 ×3, r20 ×1), counted one per quote. To these are added the run counts that r17's and r18's REPORTs state.
Gemini's quotes are not classified, because Gemini does not gate.

| passage family (sol's words) | class | record that sets it | instances (version: runs) |
|---|---|---|---|
| Data availability, release package ("A candidate release package …", "Rerunning the packaged files …") | a | Joseph's protected text (`DECISION-20261021-joseph-da-and-note-records.md:7-8,33-43`; `DECISION-20261028-joseph-protections-n4-release-retrospective.md:47-48`) | r12 3; r12-sol2 2; r13 3; r18 2; r19 2; r20 1 |
| VII C: the budget extension, with the design statement ("decided with observed p values visible") | a | `DECISION-20261004-s5p-production-budget-extension.md:64-66`; `DECISION-20261025-joseph-r18-history-to-note.md:41-47` | r12 3; r12-sol2 2; r13 1; r14 1; r17 3; r18 2 |
| VII C: the lost pseudo-experiments, rerun ("224 for calibration, 53 for power") | a | required disclosures, `DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md:117-125`; r18 decision `:44-47` | r13 2; `4ba0dd2f` 3 |
| VI: the binned diagnostic's scope ("… lie outside its scope") | a, borderline b | `DECISION-20261023-joseph-5d-a-and-register-round.md:45-46`: kept because its record requires it (`r15/REPORT.md:43-47`) | r13 3; r19 1 |
| "is being moved to the refined estimator" | a | `DECISION-20261023-joseph-2d-refined-integrate-ci.md:36` (`r16/ledger.md:49`) | r16 (count not recorded) |
| VII E: hydrocarbon replays "descriptive … do not re-grade" | b, borderline a | restored by the r13 review (MI:617-619); KEEP "descriptive" (`register-prd-study/REPORT.md:492`); the note's form is Joseph's (`DECISION-20261020-joseph-nuwro-ch-claim.md:37`) | r12 2; r12-sol2 1; `4ba0dd2f` 3; r14 3; r17 2 |
| III: the five-iteration rule | b | restored by the r12 and r13 reviews (MI:536,620-621) | r12-sol2 1; `4ba0dd2f` 2; r14 1; r19 2; r20 1 |
| IV B: the rebuilt band's post hoc rescoring | b | the r13 review (MI:621); bound by Table I and `check_sec4_receipts.py` (`r16/REPORT.md:54`) | r12 1; r14 1; r17 3 |
| Scope sentence (central values; no validated five-observable measurement; "not of multidimensional OmniFold in general") | b | KEEP negatives (`register-prd-study/REPORT.md:313-315`); r17 review b1-R1 (`r17/REPORT.md:73-74`) | `4ba0dd2f` 1; r19 1; r20 1 |
| Seed pair ("On the one seed pair measured …") | b | KEEP (`register-prd-study/REPORT.md:577`) | r14 1 |
| Design fixed after the reviewers' look (without the budget) | b | the lane's KEEP id D1 (`r17/changes.md:79`); moved to the note in r18 (`r18/REPORT.md:42`) | r14 1 |
| Fake-data listing rule, with "6 further truths are ungraded" | b | cutting the ungraded clause makes the sentence false as read (`fived16/prd-read/REPORT.md:87`) | r19 1 |
| Gaussian-fit detail of the miscoverage diagnosis | c | R4 sends this detail to the note (`register-prd-study/REPORT.md:340-341`) | r14 1 |
| Limitations lead ("… stated with the results they qualify …") | c | lane prose | r19 1 |
| "The note's calibrated tests show the same pull" | c | lane prose (the r19 Discussion) | r19 1 |
| III: the configuration paragraph and the configuration (f) lines | c, held | registry-cited lines kept byte-identical by the director's Q3 ruling (`r18/REPORT.md:167-168,186-187`) | r17 1; r18 3 |
| V D: "The covariance of the five-observable central value …" | c | lane prose | r18 1 |

**Counts:**

| population | (a) | (b) | (c) | total |
|---|---:|---:|---:|---:|
| the 54 quotes in the committed files | 27 | 24 | 3 | 54 |
| plus r17's and r18's stated run counts | 34 | 29 | 8 | 71 |
| r15 and r16 passages (no run counts) | 4 | 5 | 0 | 9 passages |

- **Borderline cases.** With the binned diagnostic as (b), the committed files give 23 / 28 / 3. With the hydrocarbon
  sentence as (a), they give 36 / 15 / 3. Either way, (a) and (b) together are 51 of 54.
- **The 8 (c) instances** include 4 that a director's ruling held fixed for a round (the registry-cited lines at r17
  and r18). Ordinary prose that the lane was free to change accounts for 4 of the 71.
- **The note's quotes are not classified here.** sol2 quoted 69 distinct passages on n2's text. n3's outline sorts them
  as stacked qualification 38, history 28 and provenance 20 (`note-n3/outline.md:24-32`). Assigning them to (a)–(c)
  would need each passage's governing record, and this report did not do that work.

### 3.3 Removing a quoted passage

**Five passages left the paper, and each stopped being quoted:**

| passage | how it left | quoted before | quoted after |
|---|---|---|---|
| Data availability | shortened, facts to the note (PR #212) | r13 3/3 | `4ba0dd2f` 0/3, r14 0/3; not named for r15–r17 |
| Lost-pseudo-experiment counts | to note §10.6 in r14 (MI:724) | `4ba0dd2f` 3/3 | r14 0/3 (r14 was not adopted, and the passage is back in r15's list) |
| IV B earlier and rebuilt bands | to the note in r18 | r17 3/3 | 0 in r18, r19 and r20 |
| VII C and VII E | to the note in r19 | r18 2/3 (VII C) | 0 in r19 and r20 |
| Configuration (f) lines | to the note in the configuration move (#413) | r18 3/3 | r19 0 |

**P1 stayed at 3 each time, because the three slots refilled.** The clearest case is the Data availability text:
- Its section of `main_paper.tex` has the same md5 at `4ba0dd2f`, `177bf84b`, `927f40bf`, `f0b26234` and `e270db89`.
- It was named in no list from r14 to r17, while stronger targets were still in the paper.
- It returned at r18 (2 of 3 runs), after r18 had moved the band history out.

**Rewording in place was weaker:**
- **Hydrocarbon sentence.** Reworded in r13 and r16, it was still quoted at r17 (2 of 3). r18's plainer wording ended
  it.
- **Five-iteration rule.** Reworded in r13, r16, r19 and r20, it was quoted again in its new forms at r19 and r20.
- **VII C.** Reordered or reworded in r13, r14, r16, r17 and r18, it was named in every list from r12 to r18.

### 3.4 Why the pairwise kept preferring the new version

- **The two instruments measure different things.** P2 is relative and resolves small changes. P1 is absolute, on a
  half-point grid, and its level-3 description matches the paper's remaining caveat density (§3.1).
- **The anchors are one half-step away.** Published PRD papers scored 3.5, 3.5 and 4.0 with sol
  (`rater-calibration/REPORT.md:71-73`). To reach 3.5 the paper must cross a whole rubric level. Through r11–r20 it
  stayed at the level whose description begins "stacked qualifiers …".
- **The text P1 objects to is mostly required.** 51 of the 54 quotes are (a) or (b) (§3.2). A round that keeps those
  passages can make the prose cleaner, which P2 sees, without leaving level 3.

---

## 4. Repeatable operations

**Repeatable and transferable.** Each can be written as an instruction, and most already are: `WRITER-BRIEF.md`;
R1–R10 at `register-prd-study/REPORT.md:305-380`; R-P1–R-P9 and R-N1–R-N7 at `caveat-study/REPORT.md:299-324`.
1. **Move histories, records and procedure to the companion, with a pointer, after proving the fact prints there.**
   - It removed every passage it was applied to from the quote list (§3.3).
   - It won every pairwise test it was part of.
   - It gave the note's only P1N gain beyond noise (MI:911-912).
2. **Rewrite from a one-sentence-per-paragraph reverse outline and a fact ledger,** by a writer with no history of the
   text. It drew the clearest pairwise preferences on both documents (§2).
3. **Give each caveat and scope statement one home; the other sites point to it.** It won in r15, r18 and n1. It lost
   in n3's summaries, which n1 had already consolidated.
4. **Split an overloaded sentence into a result and an exception;** use a list or a lead clause where a split would
   repeat the subject. prd-read Q3 shows the preference (24 of 24), and n2's §11 shows the failure mode (below).
5. **State status, not chronology** (R-N3a, R-P3). It is a sentence-level rule, and the history it removes must print
   elsewhere.

**One-offs.** Each of these was a content or placement decision that changed what the rater saw, not a writing method:
- the records move (one decision, done once);
- the Data availability shortening (Joseph's text);
- the D-ID addition;
- the configuration move;
- the citation thinning;
- the 5D integration.

**Backfired:**
- **r14, "scope inside the claim":** 1 of 4 (MI:738-743).
- **r20, rewording the six quoted passages:** 2 of 4. Gemini preferred r19, citing r20's own wording
  (`r20/REPORT.md:33-38`).
- **n2's mechanical splits in §11:** 0 of 4, "choppy and repetitive" (`note-n2/REPORT.md:144`).
- **n1's full rewrite of App. A:** 1 of 4; the base was "shorter and sequential" (`note-n1/REPORT.md:125`). n2's
  rewrite of only the six quoted passages won 4 of 4 (`note-n2/REPORT.md:142`).
- **n3's second pass on the summaries:** ES/§1 and §12 won 1 of 4 each (`note-n3/REPORT.md:103,111`).
- **Adopting rater rewrites.**
  - Gemini's rewrites invented facts in r9–r12 (MI:278-280,399-402,594-595).
  - In the clause read, every Gemini form that dropped a limitation (8) failed the guardrail, against 2 failing sol2
    forms (`fived16/prd-read/REPORT.md:111-113`).

**On encoding the operations (the DSPy question):**
- **The operations are already encoded as briefs.** The open question is the metric an optimizer would climb.
- **P1 gives it nothing to climb.** It returned 3 in 39 of 39 runs on 13 versions of the paper (§1.1), with a
  run-to-run SD of 0 over that span.
- **P2 has signal, with three limits:**
  - it rewards surface polish (`rater-calibration/REPORT.md:87-90`);
  - it has no before-against-before control (MI:922);
  - Gemini showed position bias in r14 (MI:741).
- **The guardrail is in neither metric.** Every round's independent review found real errors, typically 1–4 blocking
  findings per batch (`register-method/HANDOFF.md:26,119`). An optimizer scored on P2 alone would select for the
  rewrites those reviews reject.

---

## 5. What the evidence says about next steps for P1

These are options, each with its evidence. Joseph decides. Item 1 of DECISION-20261028 already asks for the inventory
of his protections.

1. **Remake the protections that the quotes land on** (item 1's inventory).
   - *For:* (a) is half the committed quotes (27 of 54). Every passage that left the paper stopped being quoted (§3.3).
   - *Against:* the slots refill from (b). The Data availability text returned at r18 once other targets had left.
     Removing every (a) passage would still leave the 24 (b) quotes in the same files.
2. **Reduce content: move secondary results to the note with their qualifiers** (R-P9, R-N7).
   - *For:* both caveat studies name this as the only route to the comparators' density
     (`caveat-study/REPORT.md:311,324`). For the note, consolidation and rewriting cannot reach it
     (`note-n3/REPORT.md:162-164`).
   - *Against:* r19 was a partial test. It moved the calibrated tests out and cut the paper by 29% (10,381 → 7,404
     blinded words), and P1 stayed at 3, 3, 3.
3. **Change or extend the instrument.**
   - P1N on chapter pieces scored the r12 paper 3.5, 3.5 (`NOTE-BASELINE.md:25,32-33`), with framing and splitting
     confounded.
   - More P1 runs cannot resolve a text that scores 3 in every run.
   - Any new instrument needs the anchors re-scored under it before it can set a target
     (`rater-calibration/REPORT.md:113-116`).
4. **A mechanical copy-edit pass to APS style** (numerals, serial commas, punctuation).
   - *For:* it is cheap, and Gemini's r20 reasons name exactly these points (`r20/REPORT.md:33-38`).
   - *Against:* no round so far has been a copy-edit pass on its own, so its effect on P1 is unknown. The calibration
     says P2 already rewards it.
     <!-- absence-ok: refers to the rounds tabulated in §1.1; not a claim about results elsewhere -->
5. **Stop model-scored register work on the paper, and read it.**
   - The paper's stop rule is met, and its rounds are closed (`r20/REPORT.md:29,47`).
   - At that point the method's own stop rule hands the document to human readers
     (`register-method/HANDOFF.md:28-29`).
   - n4 is the note's last round (`DECISION-20261028-joseph-protections-n4-release-retrospective.md:35-36`).
6. **For n4's front matter** (already decided), the nearest evidence:
   - n1's consolidation of the ES (−498 words) won P2N 4 of 4 and left P1N at 3, 3 (`note-n1/REPORT.md:61,109,147`);
   - n3's further pass on the same pieces won 1 of 4 (`note-n3/REPORT.md:103`).

---

## 6. Records that disagree

1. **r19's quote counts.** `r19/REPORT.md:130-133` gives the five-iteration sentence in 3 of 3 runs and the
   Limitations lead in 2 of 3. The committed raw files give 2 of 3 and 1 of 3:
   - `r19/measure/P1__r1__sol2.txt` quotes the Limitations lead (`:3`), the five-iteration sentence (`:7`) and "the
     note's calibrated tests" (`:13`);
   - `P1__r2__sol2.txt` quotes the five-iteration sentence (`:3`), the listing rule (`:9`) and the release package
     (`:15`);
   - `P1__r3__sol2.txt` quotes the scope (`:4`), the binned diagnostic (`:7`) and the release package (`:19`).

   `measure/SHA256SUMS` covers the inputs only, not these outputs.
2. **r12's Data availability count.** MI:590 says sol quoted the release bookkeeping in 2 of 3 runs. All three quote
   it:
   - `r12/scores/P1__r12__sol__r1.txt:7` and `r3.txt:14` quote "Rerunning the packaged files …";
   - `r2.txt:7` quotes "A candidate release package …".

   Both sentences are inside `\section*{Data availability}` in r12's `main_paper.tex` (`git show 5f717bf4`: the
   heading at line 148, "Rerunning" at line 174).
3. **r18's list is short by one.** `r18/REPORT.md:167-172` accounts for 8 quote instances over 3 runs of 3 quotes.
4. **A stale count in the method record.** `register-method/HANDOFF.md:20` says the paper was 3.00 "for five
   versions"; it is now 13 (§1.1).
5. **ours-old is the r8 text.** The calibration describes `1486f754` as "from before the register rounds"
   (`rater-calibration/REPORT.md:44-45`). No commit touches the paper's two sources between `1486f754` and r8's
   `e5ae5b11`. So the P1 move 2.50 → 3.00 belongs to loop 1 (r8 → r11), together with the D-ID addition.
   Search: `git log 1486f754..e5ae5b11 -- docs/analysis-note/main_paper.tex docs/analysis-note/paper_body.tex` (empty) @ 371cccecb

---

## 7. Limits

- **Few rounds per operation.** Most rounds combined several operations, so §2 attributes each round to its main
  operation. The pairwise strength is a 3-level self-report.
- **P1 granularity.** sol/sol2 score in half points, and within 3.0 ± 0.25 they show no resolution here.
- **Raw outputs for r15–r18 and r8–r11 are not committed.**
  - The r15–r18 quotes come from their REPORTs' summaries, which say the raw outputs stayed in scratchpads
    (`r15/REPORT.md:117`). §6 shows that such summaries can miscount.
  - r8–r11 used P0, and their quotes are not in the records.

  Search: QUOTE in `rater-calibration/` (only the prompt templates and `tools/analyze.py` match); `git ls-files r15 r16 r17 r18` (no P1 or score file) @ 371cccecb
- **Gemini's P1 values are not recorded for r15, r16 and r19.**
  Search: gemini; P1; RATING in `r15/REPORT.md`, `r16/REPORT.md`, `r19/REPORT.md` and `r19/measure/` (only P2 files) @ 371cccecb
- **The n2 outline, which defines R-N2a–R-N2e, is not committed.** Its moves are read here from the REPORT and from
  TeX source comments (`sec_summary.tex:5`, `sec_method.tex:89,110`).
  Search: `git ls-files note-n2` (no outline); R-N2c; R-N2d; R-N2e @ 371cccecb
- **The §3 classification is one reader's.** Its rules and borderline cases are stated so that it can be re-run.
