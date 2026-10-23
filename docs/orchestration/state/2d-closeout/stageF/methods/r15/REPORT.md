# Round r15: the methods paper under the PRD-study rules (2026-10-23)

**Governed by** `DECISION-20261023-joseph-5d-a-and-register-round.md`, items 2–3: the paper's standard is "every
printed sentence true when read with the paper's stated scope". The rules are R1–R10 and the KEEP list in
`../register-prd-study/REPORT.md`.

**Written by** a fresh writer subagent. The harness refused its own REPORT.md write, so the director committed this
record from its two final replies. The writer's other records are here: `outline.md`, `ledger.md`, `check_ledger.py`,
`changes.md` and `density.md`.

**Commits** on `stageF/register-r15-20261023`:
- `72999cc0`: the round;
- `930ee5c4`: the review fixes;
- `3f0af40c`: the tooling fix;
- plus merges of `origin/main`.

## What moved where

- **One scope paragraph in Sec. I,** in positive form, with a naming convention. It keeps the negatives that carry
  meaning:
  - no intervals of validated coverage;
  - not a validated five-observable measurement;
  - not physical exclusions;
  - no measurement uncertainty;
  - the tests are calibrated within the implemented simulation, with no recoil-response band.
- **A new Sec. VIII A, "Limitations"** (`\label{sec:limitations}`), with nine numbered items, each stated once:
  1. the 2D covariance has not been independently validated;
  2. the 2D learner was chosen after the comparison;
  3. the source of the residual bias is not established;
  4. the regularization bias is in no quoted uncertainty;
  5. the seed result rests on one seed pair;
  6. no detector-mismatch closure has been run for the (E_avail, W) map;
  7. the rejections carry over to the generators only under the sub-grid bound;
  8. the missing response band's effect on p values is unmeasured;
  9. assumption A1, and the calibration fidelity it depends on. <!-- absence-ok: these items quote the paper's own Sec. VIII A limitations, whose source lines carry the Search lines -->
- **Removed:**
  - Table I's "Principal limitation" column;
  - the conclusions' re-listing of the limitations;
  - the calibration-validity paragraph.
- **Note pointers** go from 40 to 25, about one per subsection; no pointer target was dropped. Every qualifier
  removed from the paper prints in the note (whitespace-collapsed search), and the note's own text is unchanged.
- **NuWro** leaves the abstract. Its content is unchanged in Sec. VII E.
- **The CLAIM-ADDITION out-of-scope sentence is kept,** because its record requires it.
  - `d-id/REPORT.md` §11, "Limits that travel with this outcome", lists its three items at `:545-565`, and `:7-13`
    says it is NOT CITABLE FOR an interval or a coverage result.
  - `REVERSE-OUTLINE-R2.md:140` asks for "the D-ID diagnosis, with its scope", which is also what commit
    `e97a5291` says.
- **Size:** 6,863 → 6,603 words, the abstract 135 → 115 words, and still 13 pages.

## Density (the study's tools; the reviewer reproduced every figure)

Values are before → after, per 1,000 words where a rate is given.

| measure | before | after | corpus median [range] |
|---|---|---|---|
| mean sentence length (words) | 27.9 | 25.6 | 22.7 [19.1, 28.2] |
| Q, all qualifiers | 34.1 | 29.4 | 14.4 [7.1, 26.9] |
| Q excluding negations | 23.0 | 18.2 | 10.3 [5.7, 21.5] |
| STATUS | 5.5 | 3.8 | 0.2 [0, 0.6] |
| sentences with ≥ 2 markers | 28 % | 19 % | 5 % [2, 12] |
| pointer parentheticals | 8.0 | 1.4 | 0.2 [0, 1.3] |
| strict index | 16.0 | 12.4 | 2.6 [1.3, 4.2] |

The writer deleted no true scope to move a number. What keeps the paper outside the corpus range:
- the limitations list itself;
- the KEEP-list qualifiers;
- two sentences that `check_sec4_receipts.py` binds;
- technical uses the lexicon counts.

## Independent review: ADOPT-AFTER-FIXES (nothing blocking)

**Direction A, nothing lost.**
- A scripted number inventory found nothing lost.
- Nothing printed is dropped, and no pointer target is dropped.
- Protected text is byte-identical. The only label change is the added `sec:limitations`.

**Direction B, nothing strengthened under the stated scope.** The review found five should-fix items, all now fixed:
1. The abstract now says the envelope is added **linearly**. RD2's verdict holds only under the linear sum: 9.6 % +
   1.4 % ≥ 11.0 %, against about 9.7 % in quadrature.
2. "A second, rebuilt earlier band" restores which band was rescored.
3. The deformation pointer now cites both note sections, 9.2 and 9.3.
4. The RE-1 integration ledger's base is pinned to `08fac419`, with the scope of its validity stated. r15 supersedes
   rows E17, E18 and C19.
5. The registry self-tests now find the line they test by its digest, not by line number 285.

Two smaller points were also fixed: "the study's results", and item 9 split into two sentences.

**Two notes from the review**, both outside this round:
- `app_statmethods.tex:765` says the published V is "full-rank (rank=204)". Against `tension_report.txt:13` the rank
  is 205; 204 comes from a 1e-12 threshold, and the text should state that threshold.
- The decision record's "Sec. VIII F" was corrected to the built paper's Sec. VII E.

## Blind pairwise comparison: the new version wins 4 of 4, with no order flip

- **Inputs:**
  - old: `origin/main` `177bf84b`; blinded copy sha256 `e2fb3c05…`;
  - new: `c10f178c`; blinded copy sha256 `bb6e53cc…`.
- **Routes:** sol2 (`gpt-6.1-sol`, confirmed in every log) and gemini, each in both orders. The new version won all
  four runs, at strengths 2, 1, 2 and 2.
- **The raters' reasons:**
  - a cleaner abstract;
  - the caveats consolidated into one limitations section;
  - citations as full sentences, not telegraphic tags;
  - no audit jargon such as "materiality".
- **P1 on the new version** (sol2, three runs): 3.0, 3.0 and 3.0, the same as the old paper's score. Published PRD
  anchors average 3.67.
- **What P1 still flags.** These five passages are word-for-word identical in both versions; they are the targets for
  the next round:
  - the rerun pseudo-experiments;
  - "descriptive … do not re-grade";
  - the five-iteration rule;
  - the seed panels;
  - the budget extension.
- **The data-availability block.** The old copy needed a manual repair: `pdftotext` placed part of the block inside
  the acknowledgments. The word multiset was checked unchanged, and the two versions' data-availability blocks are
  identical after normalization.
- **Raw outputs** stay in the director's scratchpad (`xmodel/r15/`).

## Checks on the final tree

- `build_all` rc 0, with every gate passing.
- The note, primer and PET note give byte-identical `pdftotext` output to `origin/main`'s.
- `swallowed_text` flags 0.
- `check_note_records`: PASS.
- The r15 ledger: 133 rows, 0 failures; its self-test catches 4 of 4 planted defects.
- The branch hook: 16 or 19 checks.
- `absence_claims --base origin/main`: 0 bare claims, 19 waivers, all in records that quote the paper.
